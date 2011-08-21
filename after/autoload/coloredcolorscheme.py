# coloredcolorscheme.vim
# Author: Eiichi Sato <sato.eiichi#gmail.com>
# Last Modified: 22 Aug 2011
# License: MIT license
#     Permission is hereby granted, free of charge, to any person obtaining
#     a copy of this software and associated documentation files (the
#     "Software"), to deal in the Software without restriction, including
#     without limitation the rights to use, copy, modify, merge, publish,
#     distribute, sublicense, and/or sell copies of the Software, and to
#     permit persons to whom the Software is furnished to do so, subject to
#     the following conditions:
#
#     The above copyright notice and this permission notice shall be included
#     in all copies or substantial portions of the Software.
#
#     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
#     CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#     TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#     SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import functools
import vim

class ColoredColorscheme(object):

    class ColorTable: # {{{
        class GnomeTerminal: # {{{
            class Tango: # {{{
                basic = [[0x00, 0x00, 0x00], [0xCC, 0x00, 0x00],
                         [0x4E, 0x9A, 0x06], [0xC4, 0xA0, 0x00],
                         [0x34, 0x65, 0xA5], [0x75, 0x50, 0x7B],
                         [0x06, 0x98, 0x9A], [0xD3, 0xD7, 0xCF],
                         [0x55, 0x57, 0x53], [0xEF, 0x29, 0x29],
                         [0x8A, 0xE2, 0x34], [0xFC, 0xE9, 0x4F],
                         [0x72, 0x9F, 0xCF], [0xAD, 0x7F, 0xA8],
                         [0x34, 0xE2, 0xE2], [0xEE, 0xEE, 0xEC]]
                values = [0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF]
            # }}}
            class Linux: # {{{
                basic = [[0x00, 0x00, 0x00], [0xAA, 0x00, 0x00],
                         [0x00, 0xAA, 0x00], [0xAA, 0x55, 0x00],
                         [0x00, 0x00, 0xAA], [0xAA, 0x00, 0xAA],
                         [0x00, 0xAA, 0xAA], [0xAA, 0xAA, 0xAA],
                         [0x55, 0x55, 0x55], [0xFF, 0x55, 0x55],
                         [0x55, 0xFF, 0x55], [0xFF, 0xFF, 0x55],
                         [0x55, 0x55, 0xFF], [0xFF, 0x55, 0xFF],
                         [0x55, 0xFF, 0xFF], [0xFF, 0xFF, 0xFF]]
                values = [0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF]
            # }}}
        # }}}
        class XTerm: # {{{
            basic = [[0x00, 0x00, 0x00], [0xCD, 0x00, 0x00],
                     [0x00, 0xCD, 0x00], [0xCD, 0xCD, 0x00],
                     [0x00, 0x00, 0xEE], [0xCD, 0x00, 0xCD],
                     [0x00, 0xCD, 0xCD], [0xE5, 0xE5, 0xE5],
                     [0x7F, 0x7F, 0x7F], [0xFF, 0x00, 0x00],
                     [0x00, 0xFF, 0x00], [0xFF, 0xFF, 0x00],
                     [0x5C, 0x5C, 0xFF], [0xFF, 0x00, 0xFF],
                     [0x00, 0xFF, 0xFF], [0xFF, 0xFF, 0xFF]]
            values = [0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF]
        # }}}
    # }}}

    colortable = ColorTable.GnomeTerminal.Linux

    class Converter(object): # {{{

        class memoized(object): # {{{
            def __init__(self, func):
                self.func = func
                self.cache = {}
            def __call__(self, *args):
                try:
                    return self.cache[args]
                except KeyError:
                    value = self.func(*args)
                    self.cache[args] = value
                    return value
                except TypeError:
                    return self.func(*args)
            def __get__(self, obj, objtype):
                return functools.partial(self.__call__, obj)
        # }}}

        def __init__(self, colortable):
            self.colortable = colortable
            self.tmp_colors = list(enumerate(map(self.index_to_rgb, range(0, 254))))

        def code_to_rgb(self, code):
            def conv(s):
                try: return int(s, 16)
                except ValueError: return 0
            return conv(code[1:3]), conv(code[3:5]), conv(code[5:7])

        def rgb_to_code(self, rgb):
            def conv(value):
                return max(min(value, 255), 0)
            return '#{0:02X}{1:02X}{2:02X}'.format(*[conv(v) for v in rgb])

        def calc_fg(self, rgb):
            if rgb[0]*30 + rgb[1]*59 + rgb[2]*11 > 12000:
                return (0, 0, 0)
            else:
                return (255, 255, 255)

        def index_to_rgb(self, index):
            if index < 16:
                return self.colortable.basic[index]
            elif 16 <= index < 232:
                index -= 16
                return [self.colortable.values[(index//36)%6],
                        self.colortable.values[(index//6)%6],
                        self.colortable.values[index%6]]
            elif 232 <= index < 256:
                return [8+(index-232)*10]*3

        @memoized
        def rgb_to_index(self, rgb):
            def diff(color):
                r = color[1][0]-rgb[0]
                g = color[1][1]-rgb[1]
                b = color[1][2]-rgb[2]
                return r*r + g*g + b*b
            best = min((color for color in self.tmp_colors), key=diff)
            return best[0]

    Converter = Converter(colortable)

    # }}}

    @staticmethod
    def add_highlight(group, color):
        converter = ColoredColorscheme.Converter
        command = 'hi {group} guifg={guifg} guibg={guibg} ctermfg={ctermfg} ctermbg={ctermbg}'

        if color[0].startswith('#'):
            bgrgb = converter.code_to_rgb(color)
            fgrgb = converter.calc_fg(bgrgb)
            command = command.format(group=group,
                                     guibg=color,
                                     guifg=converter.rgb_to_code(fgrgb),
                                     ctermbg=converter.rgb_to_index(bgrgb),
                                     ctermfg=converter.rgb_to_index(fgrgb))
        else:
            bgrgb = converter.index_to_rgb(int(color))
            bgindex = color
            fgrgb = converter.calc_fg(bgrgb)
            fgindex = converter.rgb_to_index(fgrgb)
            command = command.format(group=group,
                                     guibg=converter.rgb_to_code(bgrgb),
                                     guifg=converter.rgb_to_code(fgrgb),
                                     ctermbg=bgindex,
                                     ctermfg=fgindex)
        vim.command(command)

# vim: fdm=marker:fmr={{{,}}}
