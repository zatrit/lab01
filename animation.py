import pygame
from assets import AnimationData
from render import RenderProps
from util import LoopedTimer, empty_func
from game import UpdateData


class AnimatedSprite(pygame.sprite.Sprite):
    """Анимированный спрайт"""
    _prev_frame: int
    _prev_loop: list[pygame.Surface]
    current_frame: int
    current_loop: list[pygame.Surface]
    render_props: RenderProps

    force_redraw: bool = False

    animation_finished = empty_func

    def __init__(self, data: AnimationData, default_tag: str, rect: tuple[int, int, int, int], *groups) -> None:
        super().__init__(*groups)
        self._prev_frame = -1
        self.set_animation(data, default_tag)
        self.render_props = RenderProps()
        self.rect = rect

    def next_frame(self):
        self.current_frame += 1
        if self.current_frame % len(self.current_loop) == 0:
            self.animation_finished(self.tag)

    def tag_speed(self, tag, speed):
        self.tag_speeds[tag] = speed

    def set_animation(self, data: AnimationData, default_tag: str):
        self.tag_speeds = {}
        self.data = data
        self.timer = LoopedTimer(data.durations, self.next_frame)
        self.set_tag(default_tag)

    def set_tag(self, tag):
        if getattr(self, "tag", None) == tag:
            return False

        self.tag = tag
        start, end = self.data.tags[tag]
        self.current_loop = self.data.frames[start:end + 1]
        self.timer.set_delays(self.data.durations[start:end + 1])
        self.timer.cur_time = 0
        self.current_frame = 0
        return True

    def update(self, data: UpdateData):
        self.timer.update(data.elapsed * self.tag_speeds.get(self.tag, 1))
        frame = self.current_frame % len(self.current_loop)

        if frame != self._prev_frame or self.current_loop != self._prev_loop or self.force_redraw:
            self.image = self.render_props.apply(self.current_loop[frame])
            self.image = self.overlay(self.image)
            self._prev_frame, self._prev_loop = frame, self.current_loop
            self.force_redraw = False

    def overlay(self, image):
        return image


class PriorityAnimatedSprite(AnimatedSprite):
    def __init__(self, data: AnimationData, default_tag: str, rect: tuple[int, int, int, int], *groups) -> None:
        self.priorities: dict[str | None, int] = {}
        self.tag_priority = self.priorities.__setitem__
        super().__init__(data, default_tag, rect, *groups)

    def set_tag(self, tag, force=False):
        self_tag = getattr(self, "tag", None)
        if self.priorities.get(tag, 0) >= self.priorities.get(self_tag, 0) or force:
            return super().set_tag(tag)
        return False
