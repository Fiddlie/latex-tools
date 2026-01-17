use File::Basename;
use File::Spec;

my $root_dir = dirname(File::Spec->rel2abs(__FILE__));
$ENV{'TEXINPUTS'} = "$root_dir/classes//:$root_dir/packages//:$root_dir/lua//:" . ($ENV{'TEXINPUTS'} // '');

$pdf_mode = 4;  # Use LuaLaTeX
$lualatex = 'lualatex -interaction=nonstopmode -synctex=1 -shell-escape %O %S';

# Register yaml as an extension that latexmk should track content changes for
# This ensures manifest.yaml changes trigger rebuilds
$recorder = 1;
push @generated_exts, 'yaml';
