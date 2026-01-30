pkgname=cpuopt
pkgver=2.6.0
pkgrel=2
pkgdesc="Automatic CPU speed & power optimizer"
arch=('any')
url="https://github.com/usiqwerty/cpuopt"
license=('LGPL-3.0-or-later')
depends=('python' 'python-setuptools' 'python-psutil' 'python-distro' 'python-requests' 'python-gobject' 'python-pyinotify' 'python-urwid' 'python-pyasyncore' 'dmidecode' 'gobject-introspection')
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-poetry-core' 'python-poetry-dynamic-versioning' )
source=("git+${url}.git")
sha1sums=('SKIP')

build() {
    cd "$srcdir/${pkgname%}"
	POETRY_DYNAMIC_VERSIONING_BYPASS=1 python -m build --wheel --no-isolation
}

package() {
    cd "$srcdir/${pkgname%}"
	python -m installer --destdir="$pkgdir" dist/*.whl
	install -Dm644 $srcdir/cpuopt.service "$pkgdir/usr/lib/systemd/system/$pkgname.service"
}
