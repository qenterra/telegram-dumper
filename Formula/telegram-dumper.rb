class TelegramDumper < Formula
  desc "Terminal client for downloading permitted media from Telegram chats"
  homepage "https://github.com/QenTerra/telegram-dumper"
  url "https://github.com/QenTerra/telegram-dumper/archive/08be1b6b07ef80b14f36a75519fb087179132fee.tar.gz"
  sha256 "1b8adc2efa2c33f10c410797b556e10eba0d77947d3ac604aa0584ee75ece28a"
  version "0.2.1"
  license "MIT"

  depends_on "python@3.12"

  resource "setuptools" do
    url "https://files.pythonhosted.org/packages/a3/dc/17031897dae0efacfea57dfd3a82fdd2a2aeb58e0ff71b77b87e44edc772/setuptools-80.9.0-py3-none-any.whl"
    sha256 "062d34222ad13e0cc312a4c02d73f059e86a4acbfbdea8f8f76b28c99f306922"
  end

  resource "wheel" do
    url "https://files.pythonhosted.org/packages/0b/2c/87f3254fd8ffd29e4c02732eee68a83a1d3c346ae39bc6822dcbcb697f2b/wheel-0.45.1-py3-none-any.whl"
    sha256 "708e7481cc80179af0e556bbf0cc00b8444c7321e2700b8d8580231d13017248"
  end

  resource "jaraco-classes" do
    url "https://files.pythonhosted.org/packages/7f/66/b15ce62552d84bbfcec9a4873ab79d993a1dd4edb922cbfccae192bd5b5f/jaraco.classes-3.4.0-py3-none-any.whl"
    sha256 "f662826b6bed8cace05e7ff873ce0f9283b5c924470fe664fff1c2f00f581790"
  end

  resource "jaraco-context" do
    url "https://files.pythonhosted.org/packages/f2/58/bc8954bda5fcda97bd7c19be11b85f91973d67a706ed4a3aec33e7de22db/jaraco_context-6.1.2-py3-none-any.whl"
    sha256 "bf8150b79a2d5d91ae48629d8b427a8f7ba0e1097dd6202a9059f29a36379535"
  end

  resource "jaraco-functools" do
    url "https://files.pythonhosted.org/packages/02/36/ecc85bc96c273dc8a11273ed4782272975e6338d4a3e9228621175edf0e3/jaraco_functools-4.6.0-py3-none-any.whl"
    sha256 "99e3dc0060c5cbe8fcd1cdb36258e2a65ca40f1566b2033b12abb1bb44dd3c30"
  end

  resource "keyring" do
    url "https://files.pythonhosted.org/packages/81/db/e655086b7f3a705df045bf0933bdd9c2f79bb3c97bfef1384598bb79a217/keyring-25.7.0-py3-none-any.whl"
    sha256 "be4a0b195f149690c166e850609a477c532ddbfbaed96a404d4e43f8d5e2689f"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/c9/31/5f0ac2f1a1c67423c995c731a11cd4ad05d081a2be969d74f868bdb9cc70/markdown_it_py-4.3.0-py3-none-any.whl"
    sha256 "7aa1511a46c39138de78d9eba92ce47e63124d8003fc98b3a351909e04239efa"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/b3/38/89ba8ad64ae25be8de66a6d463314cf1eb366222074cfda9ee839c56a4b4/mdurl-0.1.2-py3-none-any.whl"
    sha256 "84008a41e51615a49fc9966191ff91509e3c40b939176e643fd50a5c2196b8f8"
  end

  resource "more-itertools" do
    url "https://files.pythonhosted.org/packages/5d/57/3c4b1c6f2e0cc29ba023802458ea3d2a996f87085559e4a5f2192d549532/more_itertools-11.2.1-py3-none-any.whl"
    sha256 "35a7377edd1dd6608dcb2cdf534ded55ea32d49448875ad042cd3f879fb1ded0"
  end

  resource "pyaes" do
    url "https://files.pythonhosted.org/packages/44/66/2c17bae31c906613795711fc78045c285048168919ace2220daa372c7d72/pyaes-1.6.1.tar.gz"
    sha256 "02c1b1405c38d3c370b085fb952dd8bea3fadcee6411ad99f312cc129c536d8f"
  end

  resource "pyasn1" do
    url "https://files.pythonhosted.org/packages/19/1f/3eefd5c84c35cae44549ce1c7f7e58f7945b34f5a6bce07a135438522073/pyasn1-0.6.5-py3-none-any.whl"
    sha256 "4017b0fce125096b8573b39c989fdb1a4b19cf761e683398184550fea0e66587"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/71/46/17f022dd3e953bf20a04a028a21ec746d942f8d2af30fa0f124fa0e6a684/pygments-2.21.0-py3-none-any.whl"
    sha256 "2363c69b61c4a97c838da3b130dcd6468f4848992b21a82f2a63ec34377137d9"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/b3/76/6d163cfac87b632216f71879e6b2cf17163f773ff59c00b5ff4900a80fa3/rich-14.3.4-py3-none-any.whl"
    sha256 "07e7adb4690f68864777b1450859253bed81a99a31ac321ac1817b2313558952"
  end

  resource "rsa" do
    url "https://files.pythonhosted.org/packages/64/8d/0133e4eb4beed9e425d9a98ed6e081a55d195481b7632472be1af08d2f6b/rsa-4.9.1-py3-none-any.whl"
    sha256 "68635866661c6836b8d39430f97a996acbd61bfa49406748ea243539fe239762"
  end

  resource "telethon" do
    url "https://files.pythonhosted.org/packages/92/ac/241c09e6905215f225d8088438ceb1f32cc4b4865f3f49068cb402debfd7/telethon-1.45.0-py3-none-any.whl"
    sha256 "339e24c83aedc9f12cbe389264627edc49779e4289c535aa90aafc4ce62f7972"
  end

  def install
    python = Formula["python@3.12"].opt_bin/"python3.12"
    system python, "-m", "venv", libexec
    pip = libexec/"bin/pip"

    resources.each do |dependency|
      dependency.stage do
        package = Pathname.pwd
        wheel = dependency.url.split("/").last
        package /= wheel if wheel.end_with?(".whl")
        system pip, "install", "--no-index", "--no-deps", "--no-build-isolation", package
      end
    end

    system pip, "install", "--no-index", "--no-deps", "--no-build-isolation", buildpath
    bin.install_symlink libexec/"bin/telegram-dumper"
  end
end
