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

Plugin 'ctrlpvim/ctrlp.vim'
Plugin 'fugitive.vim'
Plugin 'yosiat/oceanic-next-vim'
"Plugin 'mhartington/oceanic-next'
Plugin 'joukevandermaas/vim-ember-hbs'
Plugin 'airblade/vim-gitgutter'
Plugin 'tpope/vim-surround'
Plugin 'pangloss/vim-javascript'
Plugin 'scrooloose/nerdtree'
Plugin 'Xuyuanp/nerdtree-git-plugin'
Plugin 'jistr/vim-nerdtree-tabs'
Plugin 'Nopik/vim-nerdtree-direnter'
Plugin 'scrooloose/nerdcommenter'
Plugin 'elzr/vim-json'

"Plugin 'bling/vim-bufferline'
"Plugin 'weynhamz/vim-plugin-minibufexpl'
Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'

Plugin 'scrooloose/syntastic'
Plugin 'ngmy/vim-rubocop'

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

"allow backspacing over everything in insert mode
set bs=2
" keep 50 lines of command line history
set history=50
"Always show cursor position
set ruler
" Folding method
" set fdm=marker
set foldmethod=syntax
set foldlevelstart=20
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
set background=dark
"Make the completion menus readable
highlight Pmenu ctermfg=0 ctermbg=3
highlight PmenuSel ctermfg=0 ctermbg=7

""""""""""""""""""""""""""""""""""""""""""""""""
" Habit breaking, habit making
""""""""""""""""""""""""""""""""""""""""""""""""
" noremap <Up> <NOP>
" noremap <Down> <NOP>
" noremap <Left> <NOP>
" noremap <Right> <NOP>

" nnoremap <left> <nop>
" nnoremap <right> <nop>
" nnoremap <up> <nop>
" nnoremap <down> <nop>
"
" inoremap <left> <nop>
" inoremap <right> <nop>
" inoremap <up> <nop>
" inoremap <down> <nop>

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

" How to Strip Trailing Whitespace
" http://peterdowns.com/posts/strip-trailing-whitespace.html
autocmd BufWritePre <buffer> :%s/\s\+$//e

""""""""""""""""""""""""""""""""""""""""""""""""
" Highlight current line
" http://stackoverflow.com/questions/8640276/how-do-i-change-my-vim-highlight-line-to-not-be-an-underline
""""""""""""""""""""""""""""""""""""""""""""""""
set cursorline
hi CursorLine term=bold cterm=bold ctermbg=237 guibg=Grey40

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
map <C-t> :tabnew<Space>
imap <C-t> <Esc>:tabnew<Space>

" avoid finger error
map <F1> <Esc>
imap <F1> <Esc>

"map gn :bn<CR>
map gn gt
"map gp :bp<CR>
map gp gT
map gd :bd<CR>

""""""""""""""""""""""""""""""""""""""""""""""""
" CtrlP
""""""""""""""""""""""""""""""""""""""""""""""""

" Use mixed mode by default
nmap <silent> <C-p> :CtrlPMixed<CR>

" Open in new tabs by default
" https://github.com/kien/ctrlp.vim/issues/160
let g:ctrlp_prompt_mappings = {
    \ 'AcceptSelection("e")': ['<c-t>'],
    \ 'AcceptSelection("t")': ['<cr>', '<2-LeftMouse>'],
    \ }

" Exclude files and directories using Vim's wildignore and CtrlP's own g:ctrlp_custom_ignore:
set wildignore+=*/tmp/*,*.so,*.swp,*.zip     " MacOSX/Linux
set wildignore+=*\\tmp\\*,*.swp,*.zip,*.exe  " Windows

" Ignore some folders
let g:ctrlp_custom_ignore = '\v[\/](DS_Store|node_modules|bower_components|dist|coverage|tmp|electron-builds)|(\.(swp|ico|git|svn))$'
" Use .gitignore to generate ignores
" https://github.com/kien/ctrlp.vim/issues/174
let g:ctrlp_user_command = ['.git/', 'git --git-dir=%s/.git ls-files -oc --exclude-standard']
"let g:ctrlp_user_command = ['.git', 'cd %s && git ls-files . -co --exclude-standard', 'find %s -type f']

""""""""""""""""""""""""""""""""""""""""""""""""
" NERDTree{Tabs}
""""""""""""""""""""""""""""""""""""""""""""""""

" Open NERDTree on console vim startup
let g:nerdtree_tabs_open_on_console_startup = 0

" Mapping
map <Leader>n <plug>NERDTreeTabsToggle<CR>

" Open in new tab bye default
let NERDTreeMapOpenInTab='<Enter>'


""""""""""""""""""""""""""""""""""""""""""""""""
" Airline
""""""""""""""""""""""""""""""""""""""""""""""""

let g:airline#extensions#tabline#enabled = 1
let g:airline_theme='wombat'

""""""""""""""""""""""""""""""""""""""""""""""""
" Syntastic
""""""""""""""""""""""""""""""""""""""""""""""""

set statusline+=%#warningmsg#
set statusline+=%{SyntasticStatuslineFlag()}
set statusline+=%*

let g:syntastic_always_populate_loc_list = 1
let g:syntastic_auto_loc_list = 1
let g:syntastic_check_on_open = 1
let g:syntastic_check_on_wq = 0

let g:syntastic_ruby_checkers = ['rubocop']
let g:syntastic_javascript_checkers = ['eslint']

""""""""""""""""""""""""""""""""""""""""""""""""
" Misc
""""""""""""""""""""""""""""""""""""""""""""""""
" Highlight Folded
hi Folded ctermfg=14 ctermbg=0

"
set endofline

" Always show tabs
set showtabline=2

" automatically refresh any unchanged files. Also see :checktime
set autoread

" Color lines that exceed 80 columns in blue (doesn't scale)
"hi rightMargin ctermfg=lightblue
"match rightMargin /.\%>80v/

