#!/usr/bin/env bash
# Distributed under the terms of the GNU General Public License v2
# Copyright (c) 2006 Fernando J. Pereda <ferdy@gentoo.org>
#
# Git CIA bot in bash. (no, not the POSIX shell, bash).
# It is *heavily* based on Git ciabot.pl by Petr Baudis.
#
# It is meant to be run either on a post-commit hook or in an update
# hook:
#
# post-commit: It parses latest commit and current HEAD to get the
# information it needs.
#
# update: You have to call it once per merged commit:
#
#       refname=$1
#       oldhead=$2
#       newhead=$3
#       for merged in $(git rev-list ${oldhead}..${newhead} | tac) ; do
#               /path/to/ciabot.bash ${refname} ${merged}
#       done
#

# The project as known to CIA
project="drupy"

# Set to true if you want the full log to be sent
noisy=true

# Addresses for the e-mail
from="you@yourthing.com"
to="cia@cia.navi.cx"

# SMTP client to use
sendmail="/usr/sbin/sendmail -f ${from} -t ${to}"

# Changeset URL
url="http://www.example.com/gitweb/?p=${project}.git;a=commit;h=@@sha1@@"

# You shouldn't be touching anything else.
if [[ $# = 0 ]] ; then
	refname=$(git symbolic-ref HEAD 2>/dev/null)
	merged=$(git rev-parse HEAD)
else
	refname=$1
	merged=$2
fi

refname=${refname##refs/heads/}

gitver=$(git --version)
gitver=${gitver##* }

rev=$(git describe ${merged} 2>/dev/null)
[[ -z ${rev} ]] && rev=${merged:0:12}

rawcommit=$(git cat-file commit ${merged})

author=$(sed -n -e '/^author .*<\([^@]*\).*$/s--\1-p' \
	<<< "${rawcommit}")

logmessage=$(sed -e '1,/^$/d' <<< "${rawcommit}")
${noisy} || logmessage=$(head -n 1 <<< "${logmessage}")
logmessage=${logmessage//&/&amp;}
logmessage=${logmessage//</&lt;}
logmessage=${logmessage//>/&gt;}

ts=$(sed -n -e '/^author .*> \([0-9]\+\).*$/s--\1-p' \
	<<< "${rawcommit}")

out="
<message>
  <generator>
    <name>CIA Bash client for Git</name>
    <version>${gitver}</version>
    <url>http://dev.gentoo.org/~ferdy/stuff/ciabot.bash</url>
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

${sendmail} << EOM
Message-ID: <${merged:0:12}.${author}@${project}>
From: ${from}
To: ${to}
Content-type: text/xml
Subject: DeliverXML
${out}
EOM

# vim: set tw=70 :
