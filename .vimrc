""""""""""""""""""""""""""""""""""""""""""""""""
" Vundle Config http://github.com/gmarik/vundle/
""""""""""""""""""""""""""""""""""""""""""""""""
" vundle
set nocompatible               " be iMproved
filetype off                   " required!

set rtp+=~/.vim/vundle.git/
call vundle#rc()

" let Vundle manage Vundle
" required!
Bundle 'gmarik/vundle'

" My Bundles here:
"
" original repos on github
Bundle 'tpope/vim-rails'
Bundle 'msanders/snipmate.vim'
Bundle 'scrooloose/nerdtree'
" vim-scripts repos
"Bundle 'L9'
"Bundle 'FuzzyFinder'
"Bundle 'rails.vim'
" non github repos
Bundle 'git://git.wincent.com/command-t.git'
Bundle 'git://github.com/altercation/vim-colors-solarized.git'
Bundle 'git://github.com/vim-scripts/xoria256.vim.git'
" ...

filetype plugin indent on     " required!
" or
" filetype plugin on          " to not use the indentation settings set by plugins

"
" Brief help
"
" :BundleInstall  - install bundles (won't update installed)
" :BundleInstall! - update if installed
"
" :Bundles foo    - search for foo
" :Bundles! foo   - refresh cached list and search for foo
"
" :BundleClean    - confirm removal of unused bundles
" :BundleClean!   - remove without confirmation
"
" see :h vundle for more details
" Note: comments after Bundle command are not allowed..

""""""""""""""""""""""""""""""""""""""""""""""""
" Identation
""""""""""""""""""""""""""""""""""""""""""""""""
set softtabstop=2
set shiftwidth=2
set expandtab

set smartindent

"highlight current line
set cursorline
"allow backspacing over everything in insert mode
set bs=2
" keep 50 lines of command line history
set history=50
"Always show cursor position
set ruler
" Folding
set fdm=marker
"You can use the mouse to resize windows in Vim if you set your mouse as follows.
set mouse=a
"Usually annoys me
"set nowrap
"Usually I don't care about case when searching
set ignorecase
"Only ignore case when we type lower case when searching
set smartcase
"I hate noise
"set visualbell
"Show menu with possible completions
set wildmenu
"smd:   shows current vi mode in lower left
set showcmd
"ls:    makes the status bar always visible/invisible
set laststatus=2
"tf:    improves redrawing for newer computers
set ttyfast
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
    " Default theme
    colo xoria256
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

" Show line numbers
set number
set numberwidth=5

" tab navigation like firefox
map <C-t> :tabnew
imap <C-t> <Esc>:tabnew

" avoid finger error
map <F1> <Esc>
imap <F1> <Esc>

" Command-T
nmap <silent> <S-t> :CommandT<CR>
nmap <silent> <S-b> :CommandTBuffer<CR>

hi Folded ctermfg=14 ctermbg=0

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

