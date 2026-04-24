import requests
from bs4 import BeautifulSoup
import re
import json
from difflib import SequenceMatcher

# ================== 1. НАСТРОЙКИ ==================
API_KEY = 'ваш_ключ_здесь'  # ← ВСТАВЬТЕ ВАШ КЛЮЧ SCRAPERAPI
VALUE_THRESHOLD = 5.0       # минимальный валуй в % для сигнала

# ================== 2. НОРМАЛИЗАЦИЯ НАЗВАНИЙ (расширенный словарь) ==================
TEAM_SYNONYMS = {
    'anaheim ducks': 'ducks',
    'arizona coyotes': 'coyotes',
    'boston bruins': 'bruins',
    'buffalo sabres': 'sabres',
    'calgary flames': 'flames',
    'carolina hurricanes': 'hurricanes',
    'chicago blackhawks': 'blackhawks',
    'colorado avalanche': 'avalanche',
    'columbus blue jackets': 'bluejackets',
    'dallas stars': 'stars',
    'detroit red wings': 'redwings',
    'edmonton oilers': 'oilers',
    'florida panthers': 'panthers',
    'los angeles kings': 'kings',
    'minnesota wild': 'wild',
    'montreal canadiens': 'canadiens',
    'nashville predators': 'predators',
    'new jersey devils': 'devils',
    'new york islanders': 'islanders',
    'new york rangers': 'rangers',
    'ottawa senators': 'senators',
    'philadelphia flyers': 'flyers',
    'pittsburgh penguins': 'penguins',
    'san jose sharks': 'sharks',
    'seattle kraken': 'kraken',
    'st. louis blues': 'blues',
    'tampa bay lightning': 'lightning',
    'toronto maple leafs': 'mapleleafs',
    'utah mammoth': 'utah',
    'vancouver canucks': 'canucks',
    'vegas golden knights': 'goldenknights',
    'washington capitals': 'capitals',
    'winnipeg jets': 'jets',
}
# Для обратного поиска (сокращение -> возможные полные названия)
SHORT_TO_FULL = {
    'ducks': ['anaheim'],
    'coyotes': ['arizona'],
    'bruins': ['boston'],
    'sabres': ['buffalo'],
    'flames': ['calgary'],
    'hurricanes': ['carolina'],
    'blackhawks': ['chicago'],
    'avalanche': ['colorado'],
    'bluejackets': ['columbus'],
    'stars': ['dallas'],
    'redwings': ['detroit'],
    'oilers': ['edmonton'],
    'panthers': ['florida'],
    'kings': ['los angeles', 'la'],
    'wild': ['minnesota'],
    'canadiens': ['montreal'],
    'predators': ['nashville'],
    'devils': ['new jersey'],
    'islanders': ['ny islanders', 'new york islanders'],
    'rangers': ['ny rangers', 'new york rangers'],
    'senators': ['ottawa'],
    'flyers': ['philadelphia', 'philly'],
    'penguins': ['pittsburgh', 'pitt'],
    'sharks': ['san jose'],
    'kraken': ['seattle'],
    'blues': ['st. louis', 'st louis'],
    'lightning': ['tampa bay', 'tampa'],
    'mapleleafs': ['toronto'],
    'utah': ['utah mammoth'],
    'canucks': ['vancouver'],
    'goldenknights': ['vegas', 'las vegas'],
    'capitals': ['washington'],
    'jets': ['winnipeg'],
}

def normalize_team_name(name):
    """Приводит название команды к единому ключу (например, 'flyers')."""
    name = name.lower().strip()
    # Убираем лишние слова и символы
    name = re.sub(r'\b(hockey|club|team|nhl)\b', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Сначала ищем прямое совпадение в TEAM_SYNONYMS
    for full, short in TEAM_SYNONYMS.items():
        if full in name:
            return short
    # Если нет – проверяем, может это уже сокращение
    if name in SHORT_TO_FULL:
        return name
    # Попытка найти сокращение по городу
    for short, cities in SHORT_TO_FULL.items():
        for city in cities:
            if city in name:
                return short
    # Возвращаем очищенное название, если ничего не подошло
    return name.replace(' ', '')

# ================== 3. ПАРСИНГ FOREBET ==================
def get_forebet_matches():
    target_url = 'https://www.forebet.com/en/hockey/usa/nhl'
    scraper_url = f"http://api.scraperapi.com?api_key={API_KEY}&url={target_url}"
    
    print("⏳ Парсинг Forebet...")
    response = requests.get(scraper_url)
    if response.status_code != 200:
        print(f"❌ Ошибка Forebet: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    matches = soup.find_all('div', class_='rcnt')
    forebet_data = []

    for match in matches:
        try:
            match_text = match.get_text().lower()
            if any(status in match_text for status in ['ft', 'aot', 'pen.', 'finished', 'завершен']):
                continue
            if not re.search(r'\d{1,2}:\d{2}', match_text):
                continue

            home_tag = match.find('span', class_='homeTeam')
            away_tag = match.find('span', class_='awayTeam')
            if not home_tag or not away_tag:
                continue

            home = home_tag.text.strip()
            away = away_tag.text.strip()

            probs_div = match.find('div', class_='fprc')
            if not probs_div:
                continue
            probs = probs_div.find_all('span')
            if len(probs) < 2:
                continue

            prob_home = probs[0].text.strip().replace('%', '')
            prob_away = probs[-1].text.strip().replace('%', '')

            forebet_data.append({
                'home': home,
                'away': away,
                'home_norm': normalize_team_name(home),
                'away_norm': normalize_team_name(away),
                'prob_home': float(prob_home) if prob_home.isdigit() else None,
                'prob_away': float(prob_away) if prob_away.isdigit() else None
            })
        except Exception:
            continue

    print(f"✅ Найдено матчей на Forebet: {len(forebet_data)}")
    return forebet_data

# ================== 4. ПОЛУЧЕНИЕ РЫНКОВ POLYMARKET ==================
def get_polymarket_markets():
    print("\n⏳ Поиск матчей NHL на Polymarket...")
    markets_url = "https://gamma-api.polymarket.com/markets"
    params = {
        "tag_id": "899",
        "active": "true",
        "closed": "false",
        "order": "volume24hr",
        "ascending": "false",
        "limit": "100"
    }
    response = requests.get(markets_url, params=params)
    if response.status_code != 200:
        print(f"❌ Ошибка API: {response.status_code}")
        return []

    markets = response.json()
    print(f"📦 Всего рынков получено: {len(markets)}")
    
    polymarket_data = []
    for market in markets:
        question = market.get('question', '')
        if ' vs. ' not in question and ' vs ' not in question:
            continue
        
        outcomes = market.get('outcomes')
        if not outcomes or len(json.loads(outcomes) if isinstance(outcomes, str) else outcomes) != 2:
            continue
        prices = market.get('outcomePrices')
        if not prices or len(json.loads(prices) if isinstance(prices, str) else prices) != 2:
            continue
        
        # Разбираем названия
        parts = re.split(r'\s+vs\.?\s+', question, flags=re.IGNORECASE)
        if len(parts) != 2:
            continue
        team1 = parts[0].strip()
        team2 = parts[1].strip()
        
        # Парсим цены
        if isinstance(prices, str):
            prices = json.loads(prices)
        try:
            price1 = float(prices[0])
            price2 = float(prices[1])
        except:
            continue

        polymarket_data.append({
            'slug': market['slug'],
            'question': question,
            'team1': team1,
            'team2': team2,
            'team1_norm': normalize_team_name(team1),
            'team2_norm': normalize_team_name(team2),
            'price1': price1,
            'price2': price2,
            'volume_24h': float(market.get('volume24hr', 0))
        })
    
    print(f"✅ Найдено рынков NHL: {len(polymarket_data)}")
    return polymarket_data

# ================== 5. УМНОЕ СОПОСТАВЛЕНИЕ ==================
def find_matching_team(fb, pm_list):
    """Возвращает (polymarket_dict, fb_team1, fb_team2) или None"""
    fb_home_norm = fb['home_norm']
    fb_away_norm = fb['away_norm']
    
    best_match = None
    best_score = 0
    best_orientation = None
    
    for pm in pm_list:
        pm_t1_norm = pm['team1_norm']
        pm_t2_norm = pm['team2_norm']
        
        # Прямое соответствие
        score_dir = (SequenceMatcher(None, fb_home_norm, pm_t1_norm).ratio() +
                     SequenceMatcher(None, fb_away_norm, pm_t2_norm).ratio()) / 2
        # Обратное
        score_swp = (SequenceMatcher(None, fb_home_norm, pm_t2_norm).ratio() +
                     SequenceMatcher(None, fb_away_norm, pm_t1_norm).ratio()) / 2
        
        if score_dir > best_score:
            best_score = score_dir
            best_match = pm
            best_orientation = 'direct'
        if score_swp > best_score:
            best_score = score_swp
            best_match = pm
            best_orientation = 'swapped'
    
    if best_score < 0.7:   # 70% сходства
        return None
    
    if best_orientation == 'direct':
        return best_match, fb['home'], fb['away']
    else:
        return best_match, fb['away'], fb['home']

# ================== 6. АНАЛИЗ И ВЫВОД ==================
def analyze_and_display(forebet_matches, polymarket_markets):
    print("\n" + "=" * 80)
    print("РЕЗУЛЬТАТЫ СРАВНЕНИЯ")
    print("=" * 80)
    
    matched = []
    unmatched_fb = []
    used_pm = set()
    
    for fb in forebet_matches:
        result = find_matching_team(fb, polymarket_markets)
        if result is None:
            unmatched_fb.append(fb)
            continue
        pm, team1, team2 = result
        if pm['slug'] in used_pm:
            continue
        used_pm.add(pm['slug'])
        
        # Определяем вероятности Forebet для соответствующих команд
        if team1 == fb['home']:
            prob_fb1 = fb['prob_home']
            prob_fb2 = fb['prob_away']
        else:
            prob_fb1 = fb['prob_away']
            prob_fb2 = fb['prob_home']
        
        prob_pm1 = pm['price1'] * 100
        prob_pm2 = pm['price2'] * 100
        
        diff1 = prob_fb1 - prob_pm1
        diff2 = prob_fb2 - prob_pm2
        
        matched.append({
            'fb_match': f"{fb['home']} vs {fb['away']}",
            'pm_question': pm['question'],
            'team1': team1,
            'team2': team2,
            'fb_probs': (prob_fb1, prob_fb2),
            'pm_probs': (prob_pm1, prob_pm2),
            'diffs': (diff1, diff2),
            'slug': pm['slug'],
            'volume': pm['volume_24h']
        })
    
    # Вывод всех сопоставленных матчей с разницей
    print("\n📋 Все сопоставленные матчи:")
    for m in matched:
        print(f"\n{m['fb_match']}")
        print(f"   Polymarket: {m['pm_question']}")
        print(f"   Forebet: {m['fb_probs'][0]:.1f}% / {m['fb_probs'][1]:.1f}%")
        print(f"   Polymarket: {m['pm_probs'][0]:.1f}% / {m['pm_probs'][1]:.1f}%")
        print(f"   Разница: {m['team1']} Δ={m['diffs'][0]:+.1f}%, {m['team2']} Δ={m['diffs'][1]:+.1f}%")
        print(f"   Объём: ${m['volume']:.0f}")
    
    # Сигналы валуя
    print("\n" + "=" * 80)
    print("🔔 СИГНАЛЫ ВАЛУЯ (разница ≥ 5%)")
    print("=" * 80)
    signals = [m for m in matched if m['diffs'][0] >= VALUE_THRESHOLD or m['diffs'][1] >= VALUE_THRESHOLD]
    if not signals:
        print("Нет сигналов с валуем ≥ 5%.")
    else:
        for idx, m in enumerate(signals, 1):
            if m['diffs'][0] >= VALUE_THRESHOLD:
                val_team = m['team1']
                val = m['diffs'][0]
                fb_prob = m['fb_probs'][0]
                pm_prob = m['pm_probs'][0]
            else:
                val_team = m['team2']
                val = m['diffs'][1]
                fb_prob = m['fb_probs'][1]
                pm_prob = m['pm_probs'][1]
            print(f"\n#{idx} {m['fb_match']}")
            print(f"   Ставка на: {val_team}")
            print(f"   Forebet: {fb_prob:.1f}%")
            print(f"   Polymarket: {pm_prob:.1f}% (цена {pm_prob/100:.3f})")
            print(f"   Валуй: +{val:.1f}%")
            print(f"   🔗 https://polymarket.com/event/{m['slug']}")
    
    # Вывод несопоставленных матчей Forebet
    if unmatched_fb:
        print("\n" + "=" * 80)
        print("⚠️ МАТЧИ FOREBET БЕЗ ПАРЫ НА POLYMARKET")
        print("=" * 80)
        for fb in unmatched_fb:
            print(f"   - {fb['home']} vs {fb['away']}")
    
    return matched

# ================== 7. ЗАПУСК ==================
if __name__ == "__main__":
    if API_KEY == 'ваш_ключ_здесь':
        print("❌ Вставьте API-ключ ScraperAPI в переменную API_KEY.")
        exit(1)
    
    fb = get_forebet_matches()
    if not fb: exit(1)
    pm = get_polymarket_markets()
    if not pm: exit(1)
    
    analyze_and_display(fb, pm)