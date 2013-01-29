# ~/.bashrc
# by Benji Orozco

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# bash options ------------------------------------
#set -o vi                  # vi input mode
shopt -s autocd             # cd by naming directory
shopt -s cdable_vars        # if cd arg is not valid, assumes its a var defining a dir
shopt -s cdspell            # autocorrects cd misspellings
shopt -s checkwinsize       # update the value of LINES and COLUMNS after each command if altered
shopt -s cmdhist            # save multi-line commands in history as single line
shopt -s dotglob            # include dotfiles in pathname expansion
shopt -s expand_aliases     # expand aliases
shopt -s extglob            # enable extended pattern-matching features
shopt -s histappend         # append to (not overwrite) the history file
shopt -s hostcomplete       # attempt hostname expansion when @ is at the beginning of a word
shopt -s nocaseglob         # pathname expansion will be treated as case-insensitive

# set PATH so it includes user's private bin if it exists
if [ -d ~/bin ] ; then
    PATH=~/bin:"${PATH}"
fi

export MAILCHECK=0
export EDITOR="vim"
export FCEDIT="vim"
export VISUAL=$EDITOR
export PAGER=less
export LESS='-iMnQR'
export PRINTER=lp
export CVS_RSH=ssh
export HISTSIZE=2000
export HISTFILESIZE=100000
export HISTCONTROL=ignoredups
export TERM=xterm-256color
export DISPLAY=":0"

# share history across all terminals
shopt -s histappend
PROMPT_COMMAND='history -a'

# ls Color
ls --color 2> /dev/null > /dev/null
LSCOLOR="$?"
if [ "$LSCOLOR" -eq "0" ]
then
    alias ls='ls --color -C'
else
    alias ls='ls -CG'
fi

# Misc Alias.
alias gvim='gvim -p'
alias vim='vim -p'
alias vi='vim -p'
alias v='vim -p'
alias psaux='ps aux | less'
alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../..'
alias n='netstat -a -e -e -p -A inet'
alias ll='ls -l'
alias la='ls -A'
alias l='ls -CF'
alias xit='exit'
alias grep='grep --colour'
alias cl=clear
alias pamcna='pacman'
alias pacmna='pacman'

# Security Alias.
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias ln='ln -i'

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi
#http://lifehacker.com/5167879/cut-the-bash-prompt-down-to-size
PROMPT_COMMAND='DIR=`pwd|sed -e "s!$HOME!~!"`; if [ ${#DIR} -gt 30 ]; then CurDir=${DIR:0:12}...${DIR:${#DIR}-15}; else CurDir=$DIR; fi'
PS1="${debian_chroot:+($debian_chroot)}\[\033[32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\$CurDir \[\033[00m\]\$ "

# Extract Files
extract () {
  if [ -f $1 ] ; then
      case $1 in
          *.tar.bz2)   tar xvjf $1    ;;
          *.tar.gz)    tar xvzf $1    ;;
          *.tar.xz)    tar xvJf $1    ;;
          *.bz2)       bunzip2 $1     ;;
          *.rar)       unrar x $1     ;;
          *.gz)        gunzip $1      ;;
          *.tar)       tar xvf $1     ;;
          *.tbz2)      tar xvjf $1    ;;
          *.tgz)       tar xvzf $1    ;;
          *.zip)       unzip $1       ;;
          *.Z)         uncompress $1  ;;
          *.7z)        7z x $1        ;;
          *.xz)        unxz $1        ;;
          *.exe)       cabextract $1  ;;
          *)           echo "\`$1': unrecognized file compression" ;;
      esac
  else
      echo "\`$1' is not a valid file"
  fi
}

# Completion. (bash only)
complete -A alias         alias unalias
complete -A command       which
complete -A export        export printenv
complete -A hostname      ssh telnet ftp ncftp ping dig nmap
complete -A helptopic     help
complete -A job -P '%'    fg jobs
complete -A setopt        set
complete -A shopt         shopt
complete -A signal        kill killall
complete -A user          su userdel passwd
complete -A group         groupdel groupmod newgrp
complete -A directory     cd rmdir
complete -f -X '!*.@(gif|GIF|jpg|JPG|jpeg|JPEG|png|PNG|xcf|bmp|BMP|pcx|PCX)'   gimp
complete -f -X '!*.@(mp?(e)g|MP?(E)G|wma|avi|AVI|asf|vob|VOB|bin|dat|vcd|ps|pes|fli|viv|rm|ram|yuv|mov|MOV|qt|QT|wmv|mp3|MP3|ogg|OGG|ogm|OGM|mp4|MP4|wav|WAV|asx|ASX|mng|MNG|m4v)' mplayer
# If available, source the global bash completion file.
# See http://www.caliban.org/bash/index.shtml#completion for details.
if [ -f /etc/bash_completion ]; then
  . /etc/bash_completion
fi

#------------------------------------------------------------------------------
# Message.
#------------------------------------------------------------------------------
. ~/.message
