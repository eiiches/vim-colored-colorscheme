" coloredcolorscheme.vim
" Author: Eiichi Sato <sato.eiichi#gmail.com>
" Last Modified: 22 Aug 2011
" License: MIT license
"     Permission is hereby granted, free of charge, to any person obtaining
"     a copy of this software and associated documentation files (the
"     "Software"), to deal in the Software without restriction, including
"     without limitation the rights to use, copy, modify, merge, publish,
"     distribute, sublicense, and/or sell copies of the Software, and to
"     permit persons to whom the Software is furnished to do so, subject to
"     the following conditions:
"
"     The above copyright notice and this permission notice shall be included
"     in all copies or substantial portions of the Software.
"
"     THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
"     OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
"     MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
"     IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
"     CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
"     TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
"     SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

let s:cpo_save = &cpo
set cpo&vim

function! coloredcolorscheme#initialize()
	let pycode = globpath(&rtp, 'autoload/coloredcolorscheme.py')
	if has('python')
		let s:pyfile = 'pyfile'
		let s:python = 'python'
	elseif has('python3')
		let s:pyfile = 'py3file'
		let s:python = 'python3'
	else
		echoerr 'Python interface is not available.'
		finish
	endif
	execute s:pyfile pycode
endfunction
call coloredcolorscheme#initialize()

function! coloredcolorscheme#add_highlight(group, color)
	execute s:python "ColoredColorscheme.add_highlight('".a:group."', '".a:color."')"
endfunction

function! coloredcolorscheme#is_syntax_exist(pattern, group)
	redir => s:currentmatch
	silent! exe 'syn list' a:group
	redir END
	return s:currentmatch =~ escape(a:pattern, '\')
endfunction

function! coloredcolorscheme#add_syntax(color, pattern, group)
	if !coloredcolorscheme#is_syntax_exist(a:pattern, a:group)
		exe 'syntax match' a:group a:pattern 'containedin=vimHiKeyList'
		call coloredcolorscheme#add_highlight(a:group, a:color)
	endif
endfunction

function! coloredcolorscheme#add_gui_color(color, pattern)
	let group = substitute(a:color, '^#', 'vimColorGui', '')
	call coloredcolorscheme#add_syntax(a:color, '/'.a:pattern.'/', group)
endfunction

function! coloredcolorscheme#add_cterm_color(color, pattern)
	let group = 'vimColorCterm'.a:color
	call coloredcolorscheme#add_syntax(a:color, '/'.a:pattern.'/', group)
endfunction

function! coloredcolorscheme#colorize_line(where)
	let line = getline(a:where)

	" guifg and guibg
	let pattern = '\<\(guifg\|guibg\)=\(#\x\{3,6\}\)\>'
	for i in range(1, 100) " at maximum
		let found = matchlist(line, pattern, 0, i)
		if len(found) == 0 | break | endif

		if found[2] =~ '#\x\{6}$'
			call coloredcolorscheme#add_gui_color(found[2], found[0].'\>')
		elseif found[2] =~ '#\x\{3}$'
			let color = substitute(found[2], '#\(\x\)\(\x\)\(\x\)', '#\1\1\2\2\3\3', '')
			call coloredcolorscheme#add_gui_color(color, found[0].'\>')
		endif
	endfor

	" ctermfg and ctermbg
	let pattern = '\<\(ctermfg\|ctermbg\)=\(\d\+\)\>'
	for i in range(1, 100)
		let found = matchlist(line, pattern, 0, i)
		if len(found) == 0 | break | endif

		call coloredcolorscheme#add_cterm_color(found[2], found[0].'\>')
	endfor
endfunction

let &cpo = s:cpo_save
unlet s:cpo_save
