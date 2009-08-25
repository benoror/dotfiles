" my filetype file
if exists("did_load_filetypes")
    finish
endif
augroup filetypedetect
    au! BufRead,BufNewFile *.atg    setfiletype cpp 
    au! BufRead,BufNewFile *.atg    set syntax=cpp
augroup END
