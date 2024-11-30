#!/bin/sh

## Simple Check Gmail ##
## Jonny Gerold <jonny@fsk141.com> ##

# User & Password should look like the following:
## set imap_user = me@domain.tld
## set imap_pass = my_pass
### You can hardset USER & PASS here if you would like; I just
### didn't want my user/pass all over the place in conf files

USER=$(grep 'set imap_user ' ~/.mutt/muttrc | awk '{ print $4 }')
PASS=$(grep 'set imap_pass ' ~/.mutt/muttrc | awk '{ print $4 }')

# Check mail status...
function check () {
	curl -s -u $USER:$PASS https://mail.google.com/mail/feed/atom
}

# Find number of messages unread
function fullcount () {
	check |  grep '<fullcount>' | sed -e 's/<fullcount>//' -e 's/<\/fullcount>//'
}

# Print result
function print () {
if [[ -n $(fullcount) ]] && [[ $(fullcount) == '1' ]]; then
	echo "You have $(fullcount) new email!"
else
	echo "You have $(fullcount) new emails!"
fi
}

# notify-send that message!
#notify-send "$(print)"

# output number of new emails
fullcount

# static print 'You have $(fullcount) new email(s)
#print
