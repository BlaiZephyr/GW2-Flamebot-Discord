from argparse import ArgumentParser
from time import perf_counter
import grequests
import func
import codecs

from const import REQUEST_HEADERS, DPS_REPORT_JSON_URL, DEFAULT_LANGUAGE, DEFAULT_TITLE, DEFAULT_INPUT_FILE, ALL_BOSSES, ALL_PLAYERS
from models.log_class import Log
from models.boss_facto import BossFactory
from languages import LANGUES
from input import InputParser

def _make_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', required=False)
    parser.add_argument('-l', '--language', required=False, default=DEFAULT_LANGUAGE)
    parser.add_argument('-r', '--reward', action='store_true', required=False)
    parser.add_argument('-i', '--input', required=False, default=DEFAULT_INPUT_FILE)
    return parser

def debugLog(url):
    log = Log(url)
    jcontent = grequests.get(url)
    pjcontent = grequests.get(DPS_REPORT_JSON_URL, params={"permalink": url}, headers=REQUEST_HEADERS)
    responses = grequests.map([jcontent, pjcontent], size=2)
    log.set_jcontent(responses[0])
    log.set_pjcontent(responses[1])
    BossFactory.create_boss(log)
    boss = ALL_BOSSES[0]
    print(boss.start_date)
    print(boss.mvp)
    print(boss.lvp)
    #ALL_BOSSES.clear()
    #ALL_PLAYERS.clear()

def main(input_file, **kwargs) -> None:
    urls = InputParser(input_file).validate().urls
    requests = []
    for url in urls:
        requests.append(grequests.get(url))
        requests.append(grequests.get(DPS_REPORT_JSON_URL+url, headers=REQUEST_HEADERS))
    responses = grequests.map(requests, size=2*len(urls))
    logs = [Log(url) for url in urls]
    for i in range(len(urls)):
        logs[i].set_jcontent(responses[2*i])
        logs[i].set_pjcontent(responses[2*i+1])
    for log in logs:
        BossFactory.create_boss(log)
    print("\n")
    split_run_message = func.get_message_reward(ALL_BOSSES, ALL_PLAYERS, titre=DEFAULT_TITLE)

    # Remove all blanks from the text and print
    for i in range(len(split_run_message)):
        text = split_run_message[i]
        text_out = "".join([s for s in text.strip().splitlines(True) if s.strip()])
        print(text_out)


    # Write to text file
    with open("Flame_Output.txt", "w", encoding="utf-8") as f: 
        text_out = ""
        for i in range(len(split_run_message)): 
            text = split_run_message[i]
            while "\n\n" in text and i < 100:
                text = text.replace("\n\n","\n")
            text_out += text
        text_out = text_out.replace("\n\n","\n")
        f.write(text_out)


if __name__ == "__main__":
    print("Starting\n")
    start_time = perf_counter()
    
    # Language selection: 
    #
    # "EN"       : General flame
    # "EN_PMA"   : PMA, notices mechanics but doesn't flame too much.
    # "EN_short" : short and concise, doesn't really flame
    # "FR"       : French, legacy code, doesn't work anymore
    # "DE"       : German, translated by someone who doesn't know German :)
    
    LANGUES["selected_language"] = LANGUES["EN_short"]
    
    
    args = _make_parser().parse_args()
    main(args.input, reward_mode=args.reward, debug=args.debug, language=args.language)
    #debugLog("https://dps.report/YUU0-20250518-111201_cairn")
    end_time = perf_counter()
    print(f"--- {end_time - start_time:.3f} seconds ---\n")