set guifont=Terminus\ 12
set guioptions-=T "hide toolbar
set guioptions-=m "hide toolbar

" Line 1 defines the color highlighting used for n-v-c modes (set in line 3), 
" and line 2 defines a different color for insert mode (set in line 4). 
" Line 5 disables blinking (blinkon value 0) for n-v-c modes, and line 6 increases the default blink rate for insert mode. 
" Line 4 also sets the cursor shape to a 100% sized vertical bar for insert mode (the default is ver25, a 25% vertical bar).
highlight Cursor guifg=black guibg=white
highlight iCursor guifg=black guibg=lightblue
set guicursor=n-v-c:block-Cursor
set guicursor+=i:ver100-iCursor
set guicursor+=n-v-c:blinkon0
set guicursor+=i:blinkon0

hi Visual guifg=#000000 guibg=#afdfff
hi Folded guifg=#afdfff  guibg=#444444
