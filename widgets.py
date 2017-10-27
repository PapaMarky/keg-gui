import os
import pygame
import urllib

color_red = (0xb8, 0x00, 0x00)
color_green = (0x00, 0x9a, 0x00)
color_blue = (0x33, 0x3c, 0xed)
color_yellow = (0xf4, 0xdc, 0x00)
color_black = (0, 0, 0)
color_white = (255, 255, 255)
color_gray = (0x42, 0x42, 0x42)

ARIAL_FONT = None

class Widget(object):
    def __init__(self, screen):
        self._screen = screen

    def set_rect(self, x, y, w, h):
        self._rect = pygame.Rect(x, y, w, h)

    def drawMyRect(self, screen, color=color_red):
        # print 'drawMyRect: rect: {}'.format(self._rect)
        pygame.draw.rect(screen, color, self._rect, 1)

    def drawMyRectFilled(self, screen, color=color_black):
        pygame.draw.rect(screen, color, self._rect)

class WrappedText(Widget):
    def __init__(self, screen, font, x, y, w, h):
        super(WrappedText, self).__init__(screen)
        self._text = None
        self._text_image = None
        self._text_image_size = None
        self.set_rect(x, y, w, h)
        self._font = font

    # draw some text into an area of a surface
    # automatically wraps words
    # returns any text that didn't get blitted
    def drawText(self, surface, text, color, aa=False, bkg=None):
        rect = self._rect
        y = rect.top
        lineSpacing = -2

        # get the height of the font
        fontHeight = self._font.size("Tg")[1]

        while text:
            i = 1

            # determine if the row of text will be outside our area
            if y + fontHeight > rect.bottom:
                break

            # determine maximum width of line
            while self._font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1

            # if we've wrapped the text, then adjust the wrap to the last word      
            if i < len(text): 
                i = text.rfind(" ", 0, i) + 1

            # render the line and blit it to the surface
            if bkg:
                image = self._font.render(text[:i], 1, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = self._font.render(text[:i], aa, color)

            surface.blit(image, (rect.left, y))
            y += fontHeight + lineSpacing

            # remove the text we just blitted
            text = text[i:]

        return (text, image)

    def draw(self):
        # self.drawMyRect(self._screen, color=color_green)
        self.drawText(self._screen, self._text, color_white)

    def set_text(self, t):
        self._text = t
        
class TapWidget(Widget,object):
    def __init__(self, screen, tap_number):
        super(TapWidget, self).__init__(screen)
        self._number = tap_number

        self._w = w = self._screen.get_width() / 3
        self._h = h = self._screen.get_height() / 3

        self._x = x = (tap_number * w)
        self._y = y = self._screen.get_height() - h

        self.set_rect(x, y, w, h)

        self._font_size = 16
        # self._font = pygame.font.Font(ARIAL_FONT, self._font_size)
        self._font = pygame.font.Font("regular.ttf", self._font_size)

        self._served = 0
        self._full = 0
        self._name = ''

        self._description_widget = None

    def get_rect(self):
        return self._rect

    def set_info_empty(self):
        self._name = None
        self._served = 0
        self._full = 0
        self._style = ''
        self._oz_remaining = 0

    def set_info(self, info):
        if self._served == info['served'] and self._full == info['full'] and self._name == info['name']:
            return

        # source: https://www.google.com/search?q=ml+to+oz&oq=ml+to+&aqs=chrome.0.69i59j0j69i57j0l3.1487j0j7&sourceid=chrome&ie=UTF-8
        ML_TO_OZ = 0.03519505609893336
        PINT_TO_ML = 473.176
        self._served = info['served']
        self._full = info['full']
        self._name = info['name']
        self._style = info['style']
        self._description = info['description']
        self._oz_remaining = (info['full'] - info['served']) / PINT_TO_ML
#        if self._oz_remaining < 0:
#            self._oz_remaining = 0

        if self._oz_remaining > 14:
            self._oz_color = color_white
        else:
            self._oz_color = color_red

        # print 'TAP {}'.format(info['tap'])
        # print 'NAME: {}'.format(self._name)

        self.name_text = self._font.render(self._name, 1, color_white)
        self.name_pos = self.name_text.get_rect()

        s = self._font_size
        while self.name_pos.w > self._rect.w or self.name_pos.h > self._rect.h:
            s = s - 1
            font = pygame.font.Font(None, s)
            self.name_text = font.render(self._name, 1, color_white)
            self.name_pos = self.name_text.get_rect()
        x = self._rect.w / 2 - self.name_pos.w / 2
        y = self._rect.y + 10
        # self.name_pos.move_ip(x - self.name_pos.x, y - self.name_pos.y)
        xoff = (self._rect.w - self.name_pos.w) / 2
        self.name_pos.move_ip(xoff, 3)

        self._oz_text = self._font.render('{0:.1f} pints'.format(self._oz_remaining), self._font_size/2, self._oz_color)
        self._oz_pos = self._oz_text.get_rect()
        self._oz_pos.move_ip((self._rect.w - self._oz_pos.w)/2, self._rect.h - self._oz_pos.h - 3)

    def draw(self):
        if self._name is None:
            return
        #self.drawMyRectFilled(self._screen)
        self.drawMyRect(self._screen, color=color_gray)
        self._screen.blit(self.name_text, self.name_pos.move(self._rect.topleft))
        self._screen.blit(self._oz_text, self._oz_pos.move(self._rect.topleft) )

    def update(self):
        pass

class TapDetail(Widget, object):
    NAME_FONT = None
    def __init__(self, screen, tap_number, x, y, w, h):
        super(TapDetail, self).__init__(screen)
        self.set_rect(x, y, w, h)
        self._tap = tap_number
        self._margin = 10
        self._name = ''

        self._name_font_size = 24
        self._name_font = pygame.font.Font("regular.ttf", self._name_font_size)
        # self._name_font = pygame.font.Font(TapDetail.NAME_FONT, self._name_font_size)

        self._desc_font = pygame.font.Font(None, 20)

    def draw(self):
        if self._name is None:
            return

        # self.drawMyRect(self._screen, color=color_blue)
        if self._logo_scaled is not None:
            self._screen.blit(self._logo_scaled, self._rect.topleft)
        self._screen.blit(self._name_text, self._name_text_pos)
        if self._description_widget:
            self._description_widget.draw()

    def get_image(self, pic_url):
        image_cache = '/tmp/kegui'
        basename = os.path.basename(pic_url)

        # TODO(mdyer) Check for images in /home/kegbot/XXX so that we don't DL them when
        # we are on the server
        cache_path = os.path.join(image_cache, basename)
        if os.path.exists(cache_path):
            print 'CACHE HIT! {}'.format(cache_path)
            return cache_path

        front = 'http://beer.shpsec.com/media'
        url = '{}/{}'.format(front, pic_url)
        if not os.path.exists(image_cache):
            os.makedirs(image_cache)

        urllib.urlretrieve(url, cache_path)

    def set_info(self, info):
        if info is None:
            self._name = None
        if info['name'] == self._name:
            return
        self._name = info['name']

        image_path = self.get_image(info['pic_url'])

        print 'image_path: "{}"'.format(image_path)

        if os.path.exists(image_path):
            self._logo = pygame.image.load(image_path)
            w = self._rect.h

            self._logo_scaled = pygame.transform.smoothscale(self._logo, (w, w))

            x = self._logo_scaled.get_rect().x + self._logo_scaled.get_rect().w + self._margin
            y = self._rect.y
        else:
            self._logo_scaled = None
            y = self._rect.y
            x = self._rect.x + self._rect.h + self._margin

        self._name_text = self._name_font.render(self._name, 1, color_white)
        self._name_text_pos = self._name_text.get_rect()
        self._name_text_pos.move_ip(x,y)
        # print '{}: {}'.format(self._tap, info)

        w = self._rect.width - self._logo_scaled.get_rect().width - self._margin
        h = self._rect.height - self._name_text.get_rect().height
        y = self._rect.y + self._name_text_pos.h
        self._description_widget = WrappedText(self._screen, self._desc_font, x, y, w, h)
        self._description_widget.set_text(info['description'])
