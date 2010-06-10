# ~/.bashrc
# by Benji Orozco

# bash options ------------------------------------
#set -o vi                  # vi input mode
shopt -s checkwinsize       # update the value of LINES and COLUMNS after each command if altered

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# Set our environment variables
export PATH="$PATH:/usr/local/sbin:$HOME/Dropbox/bin:$HOME/.gem/ruby/1.9.1/bin:$HOME/.gem/ruby/1.8/bin"
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

#------------------------------------------------------------------------------
# Misc Alias.
#------------------------------------------------------------------------------
ls --color 2> /dev/null > /dev/null
LSCOLOR="$?"
if [ "$LSCOLOR" -eq "0" ]
then
    alias ls='ls --color -C'
else
    alias ls='ls -CG'
fi

alias vim='vim'
alias v='vim'
alias psaux='ps aux | less'
alias clear='clear'
alias cls='clear'
alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../..'
alias n='netstat -a -e -e -p -A inet'
alias cal='cal -3' #show 3 months by default
alias sudo='sudo env PATH=$PATH' #work around sudo built --with-secure-path (ubuntu)
alias apt-get='sudo apt-get'
alias aptitude='sudo aptitude'
alias ll='ls -l'
alias la='ls -A'
alias l='ls -CF'
alias xit='exit'
alias grep='grep --colour'

#------------------------------------------------------------------------------
# Security Alias.
#------------------------------------------------------------------------------
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias ln='ln -i'

#------------------------------------------------------------------------------
# Typos Alias.
#------------------------------------------------------------------------------
alias scsl=clear
alias qcls=clear
alias clls=clear
alias csl=clear
alias cll=clear
alias slc=clear
alias lcs=clear
alias lsc=clear
alias sls=clear
alias scl=clear
alias cs=clear
alias c=clear
alias cl=clear
alias ssl=clear
alias csll=clear
alias clsl=clear
alias chmdo=chmod
alias sl=ls
alias sll=ls
alias lsl=ls
alias s=ls
alias psa='ps a'
alias tarx='tar x'
alias maek=make
alias act=cat
alias cart=cat
alias grpe=grep
alias gpre=grep
alias whcih=which
alias icfonfig=ifconfig
alias ifocnfig=ifconfig
alias iv=vim
alias lvi=vim
alias vf=cd
alias vp=cp
alias nmv=mv
alias mann=man
alias nman=man
alias nmann=man
alias mb=mv
alias csv=cvs
alias nmplayer=mplayer
alias xx=exit

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi
#http://lifehacker.com/5167879/cut-the-bash-prompt-down-to-size
PROMPT_COMMAND='DIR=`pwd|sed -e "s!$HOME!~!"`; if [ ${#DIR} -gt 30 ]; then CurDir=${DIR:0:12}...${DIR:${#DIR}-15}; else CurDir=$DIR; fi'
PS1="${debian_chroot:+($debian_chroot)}\[\033[32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\$CurDir \[\033[00m\]\$ "

swap () {               # swap 2 filenames around
        if [ $# -ne 2 ]; then
                echo "swap: 2 arguments needed"; return 1
        fi
        if [ ! -e $1 ]; then
                echo "swap: $1 does not exist"; return 1
        fi
        if [ ! -e $2 ]; then
                echo "swap: $2 does not exist"; return 1
        fi
        local TMPFILE=tmp.$$ ; mv $1 $TMPFILE ; mv $2 $1 ; mv $TMPFILE $2
}

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

#------------------------------------------------------------------------------
# Completion. (bash only)
#------------------------------------------------------------------------------
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
