" Identation
set shiftwidth=2
set tabstop=2
set autoindent

"highlight current line
set cursorline 
"don't be backwards compatible with silly vi options
set nocompatible
"allow backspacing over everything in insert mode
set bs=2
" keep 50 lines of command line history
set history=50          
"Always show cursor position
set ruler
" Foldin
set fdm=marker
"You can use the mouse to resize windows in Vim if you set your mouse as follows.
set mouse=a
"This is necessary to allow pasting from outside vim. It turns off auto stuff.
"You can tell you are in paste mode when the ruler is not visible
set paste
"Usually annoys me
"set nowrap
"Usually I don't care about case when searching
set ignorecase
"Only ignore case when we type lower case when searching
set smartcase
"I hate noise
set visualbell
"Show menu with possible completions
set wildmenu
"smd:   shows current vi mode in lower left
set showcmd
"ls:    makes the status bar always visible/invisible
set laststatus=2
"tf:    improves redrawing for newer computers
set ttyfast
"smartindent moves # to start of line which is not very smart, so undo here.
:inoremap # X#
"bk:    does not write a persistent backup file of an edited file
set nobackup                    
"wb:    does keep a backup file while editing a file
set nowritebackup                 
" no swap file
set noswapfile
"lz:    will not redraw the screen while running macros (goes faster)
set lazyredraw                  
"The rest deal with whitespace handling and
"mainly make sure hardtabs are never entered
"as their interpretation is too non standard in my experience
" Dark background
set t_Co=256
"I always work on dark terminals
"set background=dark
"Make the completion menus readable
highlight Pmenu ctermfg=0 ctermbg=3
highlight PmenuSel ctermfg=0 ctermbg=7

""""""""""""""""""""""""""""""""""""""""""""""""
" Syntax highlighting
""""""""""""""""""""""""""""""""""""""""""""""""

"Syntax highlighting if appropriate
if &t_Co > 2 || has("gui_running")
    syntax on
    set hlsearch
    set incsearch "For fast terminals can highlight search string as you type
endif

if &diff
    "I'm only interested in diff colours
    syntax off
endif

"syntax highlight shell scripts as per POSIX,
"not the original Bourne shell which very few use
let g:is_posix = 1

"flag problematic whitespace (trailing and spaces before tabs)
"Note you get the same by doing let c_space_errors=1 but
"this rule really applys to everything.
highlight RedundantSpaces term=standout ctermbg=red guibg=red
match RedundantSpaces /\s\+$\| \+\ze\t/ "\ze sets end of match so only spaces highlighted
"use :set list! to toggle visible whitespace on/off
set listchars=tab:>-,trail:.,extends:>

""""""""""""""""""""""""""""""""""""""""""""""""
" Key bindings
""""""""""""""""""""""""""""""""""""""""""""""""

"allow deleting selection without updating the clipboard (yank buffer)
vnoremap x "_x
vnoremap X "_X

"<home> toggles between start of line and start of text

" Default theme
colo xoria256_benoror
"colo xoria256

" Show line numbers
set number
set numberwidth=5

" tab navigation like firefox
map <C-t> :tabnew 
imap <C-t> <Esc>:tabnew 

" avoid finger error
map <F1> <Esc>
imap <F1> <Esc>

" I love the new CursorLine, but terminal underlining kicks legibility in the nuts.
" So what to do? Bold is (extremely) subtle, but it's better than nothing.
hi CursorLine cterm=bold ctermbg=0

" Line numbers
hi LineNr ctermfg=7 ctermbg=0

" Search higlighted
hi Search cterm=bold ctermfg=0 ctermbg=3

" The default fold color is too bright and looks too much like the statusline
hi Folded ctermfg=8 ctermbg=0
hi FoldColumn cterm=bold ctermfg=8 ctermbg=0

" Statusline
" I like this better than all the reverse video of the default statusline.
hi StatusLine term=reverse cterm=bold ctermfg=16 ctermbg=12
hi StatusLineNC term=reverse cterm=bold ctermfg=2 ctermbg=8
hi User1 ctermfg=4
hi User2 ctermfg=1
hi User3 ctermfg=5
hi User4 cterm=bold ctermfg=8
hi User5 ctermfg=6
hi User6 ctermfg=2
hi User7 ctermfg=2
hi User8 ctermfg=3
hi User9 cterm=reverse ctermfg=8 ctermbg=7

" A nice, minimalistic tabline
hi TabLine cterm=none ctermfg=12 ctermbg=0
hi TabLineSel cterm=bold ctermfg=16 ctermbg=12
hi TabLineFill cterm=none ctermbg=0 ctermfg=0

" Always show tabs
set showtabline=2

" Color lines that exceed 80 columns in blue (doesn't scale)
"hi rightMargin ctermfg=lightblue
"match rightMargin /.\%>80v/

" Clear screen on exit
au VimLeave * !clear && echo "Vim closed"

" NERDTree
"filetype plugin on
"autocmd BufRead * NERDTree

" NERDTree
map <F2> :NERDTreeToggle<CR>
let NERDTreeShowBookmarks=1
