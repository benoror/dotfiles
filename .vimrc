""""""""""""""""""""""""""""""""""""""""""""""""
" Vundle
""""""""""""""""""""""""""""""""""""""""""""""""
set nocompatible              " be iMproved, required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()
" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'VundleVim/Vundle.vim'

" The following are examples of different formats supported.
" Keep Plugin commands between vundle#begin/end.
" plugin on GitHub repo
" Plugin 'tpope/vim-fugitive'
" plugin from http://vim-scripts.org/vim/scripts.html
" Plugin 'L9'
" Git plugin not hosted on GitHub
" Plugin 'git://git.wincent.com/command-t.git'
" git repos on your local machine (i.e. when working on your own plugin)
" Plugin 'file:///home/gmarik/path/to/plugin'
" The sparkup vim script is in a subdirectory of this repo called vim.
" Pass the path to set the runtimepath properly.
" Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}
" Avoid a name conflict with L9
" Plugin 'user/L9', {'name': 'newL9'}

Plugin 'yosiat/oceanic-next-vim'

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required
" To ignore plugin indent changes, instead use:
"filetype plugin on
"
" Brief help
" :PluginList       - lists configured plugins
" :PluginInstall    - installs plugins; append `!` to update or just :PluginUpdate
" :PluginSearch foo - searches for foo; append `!` to refresh local cache
" :PluginClean      - confirms removal of unused plugins; append `!` to auto-approve removal
"
" see :h vundle for more details or wiki for FAQ
" Put your non-Plugin stuff after this line


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
" Habit breaking, habit making
""""""""""""""""""""""""""""""""""""""""""""""""
noremap <Up> <NOP>
noremap <Down> <NOP>
noremap <Left> <NOP>
noremap <Right> <NOP>

nnoremap <left> <nop>
nnoremap <right> <nop>
nnoremap <up> <nop>
nnoremap <down> <nop>

inoremap <left> <nop>
inoremap <right> <nop>
inoremap <up> <nop>
inoremap <down> <nop>

""""""""""""""""""""""""""""""""""""""""""""""""
" Syntax highlighting
""""""""""""""""""""""""""""""""""""""""""""""""

"Syntax highlighting if appropriate
if &t_Co > 2 || has("gui_running")
    syntax on
    set hlsearch
    set incsearch "For fast terminals can highlight search string as you type
    " Default theme
    colorscheme OceanicNext
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

" keep cursor centered
":nnoremap <Down> jzz
":nnoremap <Up> kzz
":nnoremap j jzz
":nnoremap k kzz

" Underscore as word separator
:set iskeyword-=_

" space bar un-highligts search
:noremap <silent> <Space> :silent noh<Bar>echo<CR>

" Allows writing to files with root priviledges
cmap w!! w !sudo tee % > /dev/null

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
