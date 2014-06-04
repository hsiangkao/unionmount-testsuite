
from settings import *
from tool_box import *

declare -i filenr
filenr=100

###############################################################################
#
# Open through symlink of existing file with O_TRUNC
#
###############################################################################

# Truncate and open read-only
echo "TEST$filenr: Open(symlink->symlink) O_TRUNC|O_RDONLY"
indirect=$testdir/indirect_sym$((filenr))$termslash
direct=$testdir/direct_sym$((filenr))$termslash
file=$testdir/foo$((filenr++))$termslash

open_file -t -r $indirect -R ""
open_file -t -r $indirect -R ""

# Truncate, open write-only and overwrite
echo "TEST$filenr: Open(symlink->symlink) O_TRUNC|O_WRONLY"
indirect=$testdir/indirect_sym$((filenr))$termslash
direct=$testdir/direct_sym$((filenr))$termslash
file=$testdir/foo$((filenr++))$termslash

open_file -t -w $indirect -W "q"
open_file -r $indirect -R "q"
open_file -t -w $indirect -W "p"
open_file -r $indirect -R "p"

# Truncate, open write-only and append
echo "TEST$filenr: Open(symlink->symlink) O_TRUNC|O_APPEND|O_WRONLY"
indirect=$testdir/indirect_sym$((filenr))$termslash
direct=$testdir/direct_sym$((filenr))$termslash
file=$testdir/foo$((filenr++))$termslash

open_file -t -a $indirect -W "q"
open_file -r $indirect -R "q"
open_file -t -a $indirect -W "p"
open_file -r $indirect -R "p"

# Truncate, open read/write and overwrite
echo "TEST$filenr: Open(symlink->symlink) O_TRUNC|O_RDWR"
indirect=$testdir/indirect_sym$((filenr))$termslash
direct=$testdir/direct_sym$((filenr))$termslash
file=$testdir/foo$((filenr++))$termslash

open_file -t -r -w $indirect -W "q"
open_file -r $indirect -R "q"
open_file -t -r -w $indirect -W "p"
open_file -r $indirect -R "p"

# Truncate, open read/write and append
echo "TEST$filenr: Open(symlink->symlink) O_TRUNC|O_APPEND|O_RDWR"
indirect=$testdir/indirect_sym$((filenr))$termslash
direct=$testdir/direct_sym$((filenr))$termslash
file=$testdir/foo$((filenr++))$termslash

open_file -t -r -a $indirect -W "q"
open_file -r $indirect -R "q"
open_file -t -r -a $indirect -W "p"
open_file -r $indirect -R "p"
