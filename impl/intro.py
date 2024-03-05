import pygame_gui
import pygame
from assets import load_sound
from game import Game, RunLoop
import tomllib
from util import LoopedTimer, foreach, play_sound, play_music


def intro(game: Game):
    from impl.menu import main_menu
    from game import process_ui_events, global_event

    props = {}

    result_format = "<font color=%s> <b>%s</b></font><br>"
    props["ok"] = result_format % ("#77b02a", "OK")
    props["sound"] = result_format % (("#77b02a", "OK") if play_music(
        "assets/sound/intro.mp3") else ("#d41e3c", "FAILED"))

    frames = []
    with open("assets/data/intro.toml", "rb") as file:
        parts = tomllib.load(file)["parts"]
    for part in parts:
        part: dict
        delay = part.get("delay", 0)
        lines = part.get("lines", ("",))
        sound = part.get("sound", None)
        if isinstance(lines, str) and lines.startswith("#"):
            lines = (props[lines[1:]],)
        for line in lines:
            frames.append((delay, line, sound))
    delays, *lines = map(list, zip(*frames))
    lines = zip(*lines)

    manager = pygame_gui.UIManager(screen_size := game.screen.get_size(),
                                   "assets/data/intro_theme.json")
    manager.preload_fonts(
        [{'name': "fira_code", "point_size": 14, "style": "bold"}])

    text_box = pygame_gui.elements.UITextBox(
        "", (10, 10, *screen_size), manager=manager)

    sounds = {}

    def next_line():
        try:
            line, sound = next(lines)  # type: ignore
            if sound:
                if sound not in sounds:
                    sounds[sound] = load_sound(f"assets/sound/{sound}.mp3")
                play_sound(sounds[sound])

            text_box.append_html_text(line)
            text_box.rebuild()
        except StopIteration:
            loop.running = False

    timer = LoopedTimer(delays, next_line)

    game.screen.fill(0x050914)

    loop = RunLoop()
    while loop:
        elapsed = game.clock.tick_busy_loop(60) / 1000
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                loop.running = False

        foreach(lambda e: global_event(game, e), events)
        timer.update(elapsed)
        process_ui_events(game, manager, events)
        manager.update(elapsed)
        manager.draw_ui(game.screen)
        pygame.display.update()

    pygame.mixer.stop()
    main_menu(game)
