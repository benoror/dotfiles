if v:lang =~ "utf8$" || v:lang =~ "UTF-8$"
    set fileencodings=utf-8,latin1
endif
if v:version >= 700
    "The following are a bit slow
    "for me to enable by default
    set cursorline "highlight current line
    "set cursorcolumn "highlight current column
endif
"don't be backwards compatible with silly vi options
set nocompatible
"allow backspacing over everything in insert mode
set bs=2
set viminfo='20,\"50    " read/write a .viminfo file, don't store more
                        " than 50 lines of registers
set history=50          " keep 50 lines of command line history
"Always show cursor position
set ruler
if has("autocmd")
  " When editing a file, always jump to the last cursor position
  autocmd BufReadPost *
  \ if line("'\"") > 0 && line ("'\"") <= line("$") |
  \   exe "normal g'\"" |
  \ endif
endif
"This is necessary to allow pasting from outside vim. It turns off auto stuff.
"You can tell you are in paste mode when the ruler is not visible
set pastetoggle=<F2>
"Usually annoys me
set nowrap
"Usually I don't care about case when searching
set ignorecase
"Only ignore case when we type lower case when searching
set smartcase
"I hate noise
set visualbell
"Show menu with possible completions
set wildmenu
"Ignore these files when completing names and in Explorer
set wildignore=.svn,CVS,.git,*.o,*.a,*.class,*.mo,*.la,*.so,*.obj,*.swp,*.jpg,*.png,*.xpm,*.gif
"smd:   shows current vi mode in lower left
set showcmd
"ls:    makes the status bar always visible/invisible
set laststatus=2
"tf:    improves redrawing for newer computers
set ttyfast
"cin:   enables the second-most configurable indentation (see :help C-indenting).
set cindent
set cinoptions=l1,c4,(s,U1,w1,m1,j1
set cinwords=if,elif,else,for,while,try,except,finally,def,class

set nobackup                    "bk:    does not write a persistent backup file of an edited file
set writebackup                 "wb:    does keep a backup file while editing a file

""""""""""""""""""""""""""""""""""""""""""""""""
" Indenting
""""""""""""""""""""""""""""""""""""""""""""""""

set expandtab                   "et:    uses spaces instead of tab characters
set smarttab                    "sta:   helps with backspacing because of expandtab
set tabstop=4                   "ts:    number of spaces that a tab counts for
set shiftwidth=4                "sw:    number of spaces to use for autoindent
set shiftround                  "sr:    rounds indent to a multiple of shiftwidth

set nojoinspaces                "nojs:  prevents inserting two spaces after punctuation on a join (it's not 1990 anymore)
set lazyredraw                  "lz:    will not redraw the screen while running macros (goes faster)
set pastetoggle=<F5>            "pt:    useful so auto-indenting doesn't mess up code when pasting

set noautoindent
set smartindent
"smartindent moves # to start of line which
"is not very smart, so undo here.
:inoremap # X#

"The rest deal with whitespace handling and
"mainly make sure hardtabs are never entered
"as their interpretation is too non standard in my experience
set softtabstop=4

""""""""""""""""""""""""""""""""""""""""""""""""
" Dark background
""""""""""""""""""""""""""""""""""""""""""""""""
set t_Co=256

"I always work on dark terminals
set background=dark

"Make the completion menus readable
highlight Pmenu ctermfg=0 ctermbg=3
highlight PmenuSel ctermfg=0 ctermbg=7

"The following should be done automatically for the default colour scheme
"at least, but it is not in Vim 7.0.17.
if &bg == "dark"
  highlight MatchParen ctermbg=darkblue guibg=blue
endif

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
 "highlight RedundantSpaces term=standout ctermbg=red guibg=red
 "match RedundantSpaces /\s\+$\| \+\ze\t/ "\ze sets end of match so only spaces highlighted
"use :set list! to toggle visible whitespace on/off
 "set listchars=tab:>-,trail:.,extends:>

""""""""""""""""""""""""""""""""""""""""""""""""
" Key bindings
""""""""""""""""""""""""""""""""""""""""""""""""

"allow deleting selection without updating the clipboard (yank buffer)
vnoremap x "_x
vnoremap X "_X

"<home> toggles between start of line and start of text
imap <khome> <home>
nmap <khome> <home>
inoremap <silent> <home> <C-O>:call Home()<CR>
nnoremap <silent> <home> :call Home()<CR>
function Home()
    let curcol = wincol()
    normal ^
    let newcol = wincol()
    if newcol == curcol
        normal 0
    endif
endfunction

"<end> goes to end of screen before end of line
imap <kend> <end>
nmap <kend> <end>
inoremap <silent> <end> <C-O>:call End()<CR>
nnoremap <silent> <end> :call End()<CR>
function End()
    let curcol = wincol()
    normal g$
    let newcol = wincol()
    if newcol == curcol
        normal $
    endif
    "The following is to work around issue for insert mode only.
    "normal g$ doesn't go to pos after last char when appropriate.
    "More details and patch here:
    "http://www.pixelbeat.org/patches/vim-7.0023-eol.diff
    if virtcol(".") == virtcol("$") - 1
        normal $
    endif
endfunction

"Ctrl-{up,down} to scroll.
"The following only works in gvim?
"Also vim doesn't have default C-{home,end} bindings?
if has("gui_running")
    nmap <C-up> <C-y>
    imap <C-up> <C-o><C-y>
    nmap <C-down> <C-e>
    imap <C-down> <C-o><C-e>
endif

""""""""""""""""""""""""""""""""""""""""""""""""
" file type handling
""""""""""""""""""""""""""""""""""""""""""""""""

" Allow gf command to open files in $PYTHONPATH
let &path = &path . "," . substitute($PYTHONPATH, ';', ',', 'g')

" To create new file securely do: vim new.file.txt.gpg
" Your private key used to decrypt the text before viewing should
" be protected by a passphrase. Alternatively one could use
" a passphrase directly with symmetric encryption in the gpg commands below.
au BufNewFile,BufReadPre *.gpg :set secure viminfo= noswapfile nobackup nowritebackup history=0 binary
au BufReadPost *.gpg :%!gpg -d 2>/dev/null
au BufWritePre *.gpg :%!gpg -e -r 'benoror@gmail.com' 2>/dev/null
au BufWritePost *.gpg u

" Unbind the cursor keys in insert, normal and visual modes.
"for prefix in ['i', 'n', 'v']
"      for key in ['<Up>', '<Down>', '<Left>', '<Right>']
"            exe prefix . "noremap " . key . " <Nop>"
"       endfor
"endfor
"

" Default theme
colo xoria256

" Show line numbers
set number
set numberwidth=5

" tab navigation like firefox
map <C-t> :tabnew<CR>
imap <C-t> <Esc>:tabnew<CR>

" copy/cut/paste mappings
vmap <C-c> "+y<Esc>
nmap <C-v> "+p<CR>
vmap <C-x> "+d<Esc>

" avoid finger error
map <F1> <Esc>
imap <F1> <Esc>

" I love the new CursorLine, but terminal underlining kicks legibility in the nuts.
" So what to do? Bold is (extremely) subtle, but it's better than nothing.
hi CursorLine cterm=bold ctermbg=8

" Line numbers
hi LineNr ctermfg=7 ctermbg=8

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
hi TabLine cterm=underline ctermfg=12 ctermbg=8
hi TabLineSel cterm=none ctermfg=8 ctermbg=12
hi TabLineFill cterm=underline ctermbg=8 ctermfg=12

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

