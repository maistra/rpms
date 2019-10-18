Summary: Ninja is a small build system with a focus on speed.
Name: ninja-build
Version: 1.9.0
Release: 1%{?dist}
Group: Development/Tools
License: Apache 2.0
URL: https://github.com/ninja-build/ninja
Source0: https://github.com/ninja-build/ninja/archive/v%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  python36
BuildRequires:  asciidoc
Requires:       emacs-filesystem
Requires:       vim-filesystem

%description
Ninja is yet another build system. It takes as input the interdependencies of files (typically source code and output executables) and
orchestrates building them, quickly.

Ninja joins a sea of other build systems. Its distinguishing goal is to be fast. It is born from my work on the Chromium browser project,
which has over 30,000 source files and whose other build systems (including one built from custom non-recursive Makefiles) can take ten
seconds to start building after changing one file. Ninja is under a second.

%prep
%setup -n ninja-%{version}

%build
echo Building..
python3 ./configure.py --bootstrap
./ninja manual

%install
rm -rf %{buildroot}

install -dpm0755 %{buildroot}%{_bindir}
install -Dpm0755 ninja -t %{buildroot}%{_bindir}/
install -Dpm0644 misc/bash-completion %{buildroot}%{_datadir}/bash-completion/completions/ninja
install -Dpm0644 misc/ninja-mode.el %{buildroot}%{_datadir}/emacs/site-lisp/ninja-mode.el
install -Dpm0644 misc/ninja.vim %{buildroot}%{_datadir}/vim/vimfiles/syntax/ninja.vim
install -Dpm0644 misc/zsh-completion %{buildroot}%{_datadir}/zsh/site-functions/_ninja

ln -s ninja %{buildroot}%{_bindir}/ninja-build

%files
%license COPYING
%doc HACKING.md README doc/manual.html
%{_bindir}/ninja
%{_bindir}/ninja-build
%{_datadir}/bash-completion/completions/ninja
%{_datadir}/emacs/site-lisp/ninja-mode.el
%{_datadir}/vim/vimfiles/syntax/ninja.vim
%{_datadir}/zsh/

%changelog
* Wed Oct 16 2019 Jonh Wendell <jonh.wendell@redhat.com> - 1.9.0-1
- Updated to 1.9.0
- Use Python 3

* Tue Jul 31 2018 Dmitri Dolguikh <ddolguik@redhat.com> - 1.8.2-1
- New package
