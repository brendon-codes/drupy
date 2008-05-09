#!/bin/bash
# Distributed under the terms of the GNU General Public License v2
# Copyright (c) 2006 Fernando J. Pereda <ferdy@gentoo.org>
# Copyright (c) 2008 Leonardo Valeri Manera <l DOT valerimanera @ gmail DOT com>
#
# Git CIA bot in bash. (no, not the POSIX shell, bash).
# It is *heavily* based on Git ciabot.pl by Petr Baudis.
#
# It is meant to be run in an update hook:
#
#   refname=$1
#   oldhead=$2
#   newhead=$3
#   /path/to/ciabot.bash ${refname} ${oldhead} ${newhead} gitweb/project/name.git &
#

# The project as known to CIA
project="drupy"

# Set to true if you want the full log to be sent
noisy=true

# Addresses for the e-mail
to="cia@cia.vc"

# SMTP client to use
sendmail="/usr/sbin/sendmail ${to} -i"

# gitweb project
gitweb_project="${4:-${project}.git}"

# Changeset URL
url="http://git.einit.org/?p=${gitweb_project};a=commit;h=@@sha1@@"

# The script itself

gitver=$(git --version)
gitver=${gitver##* }

oldhead=$2
newhead=$3

refname=${1##refs/heads/}

mail_cia() {

rev=$(git describe ${merged} 2>/dev/null)
[[ -z ${rev} ]] && rev=${merged:0:12}

rawcommit=$(git cat-file commit ${merged})

author=$(grep author <<EOF
< "$rawcommit" | sed -e 's:author \(.*\) <.*:\1:')

logmessage=$(sed -e '1,/^$/d' <<EOF
< "${rawcommit}")
${noisy} || logmessage=$(head -n 1 <<EOF
< "${logmessage}")
logmessage=${logmessage//&/&amp;}
logmessage=${logmessage//</&lt;}
logmessage=${logmessage//>/&gt;}

repository=$(echo "${gitweb_project}" | sed -e 's:.*/::g' -e 's:\.git::')
logmessage=":${repository}: ${logmessage}"

ts=$(sed -n -e '/^author .*> \([0-9]\+\).*$/s--\1-p' \
    <<EOF
< "${rawcommit}")

out="
<message>
  <generator>
    <name>CIA Bash client for Git</name>
    <version>${gitver}</version>
    <url>http://jyujin.de/~creidiki/ciabot.bash</url>
  </generator>
  <source>
    <project>${project}</project>
    <branch>${refname}</branch>
  </source>
  <timestamp>${ts}</timestamp>
  <body>
    <commit>
      <author>${author}</author>
      <revision>${rev}</revision>
      <files>
        $(git diff-tree -r --name-only ${merged} |
          sed -e '1d' -e 's-.*-<file>&</file>-')
      </files>
      <log>
${logmessage}
      </log>
      <url>${url//@@sha1@@/${merged}}</url>
    </commit>
  </body>
</message>"

${sendmail} <<EOF
 EOM
Message-ID: <${merged:0:12}.${author}@${project}>
From: ${from}
To: ${to}
Content-type: text/xml
Subject: DeliverXML
${out}
EOM

}

for merged in $(git rev-list ${oldhead}..${newhead} | tac); do
    mail_cia
done

# vim: set tw=70 :
