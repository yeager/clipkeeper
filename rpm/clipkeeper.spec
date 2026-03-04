%global pypi_name clipkeeper

Name:           clipkeeper
Version:        0.1.1
Release:        1%{?dist}
Summary:        GTK4 clipboard manager for Linux

License:        GPL-3.0+
URL:            https://github.com/yeager/clipkeeper
Source0:        %{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
Requires:       python3-gobject
Requires:       gtk4
Requires:       libadwaita

%description
ClipKeeper is a modern clipboard manager built with GTK4 and libadwaita.
It provides a clean interface to manage your clipboard history with features
like pinning important entries, searching, and keyboard shortcuts.

Features include:
- Clean, modern GTK4/Adwaita interface
- Clipboard history with search
- Pin important entries
- Keyboard shortcuts
- Command-line interface
- Automatic startup support

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%py3_build

%install
%py3_install

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/clipkeeper
%{_bindir}/clipkeeper-gui
%{python3_sitelib}/%{pypi_name}/
%{python3_sitelib}/%{pypi_name}-%{version}-py%{python3_version}.egg-info/

%changelog
* Tue Mar 04 2025 Daniel Nylander <daniel@danielnylander.se> - 0.1.0-1
- Initial release