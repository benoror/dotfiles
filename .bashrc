# ~/.bashrc
# by Benji Orozco

# $PATH
export PATH="$PATH:/usr/local/sbin:/usr/sbin:/sbin:$HOME/bin:$HOME/.gem/ruby/1.8/bin"

# Set our environment variables
export MAILCHECK=0
export EDITOR=vim
export VISUAL=$EDITOR
export PAGER=less
export LESS='-iMnQR'
export PRINTER=lp
export CVS_RSH=ssh
export HISTSIZE=2000
export HISTFILESIZE=100000
export HISTCONTROL=ignoredups

# Misc settings
bind 'C-u:kill-whole-line'			# Ctrl-U kills whole line
#bind 'set show-all-if-ambiguous on'           	# Tab once for complete
#bind 'set visible-stats on'                    # Show file info in complete

# Alias

alias vim='vim'
alias v='vim'
alias vi='vim'
alias psaux='ps aux | less'
alias cls='clear'
alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../..'
alias n='netstat -a -e -e -p -A inet'
alias cal='cal -3' #show 3 months by default
alias sudo='sudo env PATH=$PATH' #work around sudo built --with-secure-path (ubuntu)
alias pacman='echo -e "\n\t+Using yaourt instead\n"; yaourt'
alias apt-get='sudo apt-get'
alias aptitude='sudo aptitude'

# enable color support of ls and also add handy aliases
if [ "$TERM" != "dumb" ]; then
    alias ls='ls -G'
    alias ll='ls -l'
    alias la='ls -A'
    alias l='ls -CF'
    alias grep='grep --colour'
fi


# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

#http://lifehacker.com/5167879/cut-the-bash-prompt-down-to-size
PROMPT_COMMAND='DIR=`pwd|sed -e "s!$HOME!~!"`; if [ ${#DIR} -gt 30 ]; then CurDir=${DIR:0:12}...${DIR:${#DIR}-15}; else CurDir=$DIR; fi'
PS1="${debian_chroot:+($debian_chroot)}\[\033[32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\$CurDir \[\033[00m\]\$ "

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# Functions
findgrep () {           # find | grep
        if [ $# -eq 0 ]; then
                echo "findgrep: No arguments entered."; return 1
        else
                # "{.[a-zA-Z],}*" instead of "." makes the output cleaner
                find {.[a-zA-Z],}* -type f | xargs grep -n $* /dev/null \
                                2> /dev/null
        fi
}

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

#------------------------------------------------------------------------------
# Completion.
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

# If available, source the global bash completion file.
# See http://www.caliban.org/bash/index.shtml#completion for details.
if [ -f /etc/bash_completion ]; then
  . /etc/bash_completion
  fi

  complete -f -X '!*.@(gif|GIF|jpg|JPG|jpeg|JPEG|png|PNG|xcf|bmp|BMP|pcx|PCX)'   gimp
  complete -f -X '!*.@(mp?(e)g|MP?(E)G|wma|avi|AVI|asf|vob|VOB|bin|dat|vcd|ps|pes|fli|viv|rm|ram|yuv|mov|MOV|qt|QT|wmv|mp3|MP3|ogg|OGG|ogm|OGM|mp4|MP4|wav|WAV|asx|ASX|mng|MNG|m4v)' mplayer

#------------------------------------------------------------------------------
# Security.
#------------------------------------------------------------------------------
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias ln='ln -i'

#------------------------------------------------------------------------------
# Typos.#------------------------------------------------------------------------------
# Typos.
#------------------------------------------------------------------------------
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

# KEYCHAIN
#/usr/bin/keychain -Q -q ~/.ssh/id_rsa
#[[ -f $HOME/.keychain/$HOSTNAME-sh ]] && source $HOME/.keychain/$HOSTNAME-sh

#------------------------------------------------------------------------------
# Message.
#------------------------------------------------------------------------------
cat ~/.message

if [ "$COLORTERM" == "gnome-terminal" ]; then
        export TERM=xterm-256color
fi 
