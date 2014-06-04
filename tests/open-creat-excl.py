
from settings import *
from tool_box import *

declare -i filenr
filenr=100

###############################################################################
#
# Open of existing file with O_CREAT and O_EXCL
#
###############################################################################

# Open read-only
echo "TEST$filenr: Open O_CREAT|O_EXCL|O_RDONLY"
file=$testdir/foo$((filenr++))$termslash

open_file -c -e -r $file -E EEXIST
open_file -r $file -R ":xxx:yyy:zzz"

# Open write-only and overwrite
echo "TEST$filenr: Open O_CREAT|O_EXCL|O_WRONLY"
file=$testdir/foo$((filenr++))$termslash

open_file -c -e -w $file -E EEXIST
open_file -r $file -R ":xxx:yyy:zzz"

# Open write-only and append
echo "TEST$filenr: Open O_CREAT|O_EXCL|O_APPEND|O_WRONLY"
file=$testdir/foo$((filenr++))$termslash

open_file -c -e -a $file -E EEXIST
open_file -r $file -R ":xxx:yyy:zzz"

# Open read/write and overwrite
echo "TEST$filenr: Open O_CREAT|O_EXCL|O_RDWR"
file=$testdir/foo$((filenr++))$termslash

open_file -c -e -r -w $file -E EEXIST
open_file -r $file -R ":xxx:yyy:zzz"

# Open read/write and append
echo "TEST$filenr: Open O_CREAT|O_EXCL|O_APPEND|O_RDWR"
file=$testdir/foo$((filenr++))$termslash

open_file -c -e -r -a $file -E EEXIST
open_file -r $file -R ":xxx:yyy:zzz"
