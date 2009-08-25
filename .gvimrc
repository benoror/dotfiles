"Note MiscFixed is not antialiased which is redundant for
"unscaled bitmap fonts in my opinion and just slows things down
"and makes it harder to read. It's a nice font also.
set guifont=Terminus\ 12
set columns=160 lines=50
"set guioptions-=T "hide toolbar


syntax on

"Try to load happy hacking teal colour scheme
"I copy this to ~/.vim/colors/hhteal.vim
" silent! colorscheme murphy
" silent! colorscheme slate
silent! colorscheme default
if exists("colors_name") == 0
    "Otherwise modify the defaults appropriately

    "background set to dark in .vimrc
    "So pick appropriate defaults.
    hi Normal     guifg=gray guibg=black
    hi Visual     gui=none guifg=black guibg=yellow

    "The following removes bold from all highlighting
    "as this is usually rendered badly for me. Note this
    "is not done in .vimrc because bold usually makes
    "the colour brighter on terminals and most terminals
    "allow one to keep the new colour while turning off
    "the actual bolding.

    " Steve Hall wrote this function for me on vim@vim.org
    " See :help attr-list for possible attrs to pass
    function! Highlight_remove_attr(attr)
        " save selection registers
        new
        silent! put

        " get current highlight configuration
        redir @x
        silent! highlight
        redir END
        " open temp buffer
        new
        " paste in
        silent! put x

        " convert to vim syntax (from Mkcolorscheme.vim,
        "   http://vim.sourceforge.net/scripts/script.php?script_id=85)
        " delete empty,"links" and "cleared" lines
        silent! g/^$\| links \| cleared/d
        " join any lines wrapped by the highlight command output
        silent! %s/\n \+/ /
        " remove the xxx's
        silent! %s/ xxx / /
        " add highlight commands
        silent! %s/^/highlight /
        " protect spaces in some font names
        silent! %s/font=\(.*\)/font='\1'/

        " substitute bold with "NONE"
        execute 'silent! %s/' . a:attr . '\([\w,]*\)/NONE\1/geI'
        " yank entire buffer
        normal ggVG
        " copy
        silent! normal "xy
        " run
        execute @x

        " remove temp buffer
        bwipeout!

        " restore selection registers
        silent! normal ggVGy
        bwipeout!
    endfunction
    autocmd BufNewFile,BufRead * call Highlight_remove_attr("bold")
    " Note adding ,Syntax above messes up the syntax loading
    " See :help syntax-loading for more info
endif
highlight Pmenu guibg=yellow guifg=black
highlight PmenuSel guibg=white guifg=black

colo xoria256
set guioptions-=T
