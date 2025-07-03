# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running ‘nixos-help’).

{ config, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix  
      #<home-manager/nixos> # ToDo
    ];

  # Bootloader and Kernel version.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  # boot.kernelPackages = pkgs.linuxPackages_latest;

  networking.hostName = "nixos"; # Define your hostname.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Enable networking
  networking.networkmanager.enable = true;

  # Set your time zone.
  time.timeZone = "America/Monterrey";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";

  # Enable the X11 windowing system.
  services.xserver.enable = true;

  # Virtualisation settings.
  # QEMU (UTM MacOs) # ToDo: qemu_utm_macos.nix
  # https://discourse.nixos.org/t/nixos-as-a-guest-os-in-qemu-kvm-how-to-share-clipboard-displaying-scaling-etc/8124
  # https://discourse.nixos.org/t/qemu-kvm-copy-paste/31247
  # https://discourse.nixos.org/t/adding-virtio-drivers-to-nixos-configuration/47217
  # https://codeberg.org/Dimitris98/NixOS-dotfiles/src/branch/main/nixos/configuration.nix
  # https://nixos.wiki/wiki/Libvirt\
  # https://wiki.nixos.org/wiki/Libvirt

  # services.xserver.videoDrivers = [ "qxl" ];

  services = {
    qemuGuest.enable = true;
    spice-vdagentd.enable = true;
    spice-webdavd.enable = true;
  };

  # virtualisation = {
  #   libvirtd = {
  #     enable = true;
  #     #guestAgent.enable = true;
  #     qemu = {
  #       ovmf.enable = true;
  #       ovmf.packages = [ pkgs.OVMF.fd ];
  #       swtpm.enable = true;
  #     };
  #   };
  #   spiceUSBRedirection.enable = true;
  # };

  # virtualisation.libvirtd = {
  #   enable = true;
  #   qemu = {
  #     package = pkgs.qemu_kvm;
  #     runAsRoot = true;
  #     swtpm.enable = true;
  #     ovmf = {
  #       enable = true;
  #       packages = [(pkgs.OVMF.override {
  #         secureBoot = true;
  #         tpmSupport = true;
  #       }).fd];
  #     };
  #   };
  # };

  services.davfs2 = {
    enable = true;
    settings.globalSection.ask_auth = 0;
  };
  
  fileSystems = {
    "/mnt/macos" = {
      device = "http://localhost:9843/";
      fsType = "davfs";
      options = [
      	"users"  # Allows any user to mount and unmount
	"nofail" # Prevent system from failing if this drive doesn't mount
	"x-gvfs-show" # Making disk visible in your file explorer (ie GNOME Nautilus)
      ];
    };
  };

  # Enable the GNOME Desktop Environment.
  services.xserver.displayManager.gdm.enable = true;
  services.xserver.desktopManager.gnome.enable = true;

  # Configure keymap in X11
  services.xserver.xkb = {
    layout = "us";
    variant = "";
  };

  # Enable CUPS to print documents.
  # services.printing.enable = true;

  # Enable sound with pipewire.
  hardware.pulseaudio.enable = false;
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
    # If you want to use JACK applications, uncomment this
    #jack.enable = true;

    # use the example session manager (no others are packaged yet so this is enabled by default,
    # no need to redefine it in your config for now)
    #media-session.enable = true;
  };

  # Enable touchpad support (enabled default in most desktopManager).
  # services.xserver.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.benoror = {
    isNormalUser = true;
    description = "Ben Orozco";
    extraGroups = [ "networkmanager" "wheel" "libvirtd" ];
    packages = with pkgs; [
      ghostty
      neovim
    ];
  };

  # Enable automatic login for the user.
  services.displayManager.autoLogin.enable = true;
  services.displayManager.autoLogin.user = "benoror";

  # Workaround for GNOME autologin: https://github.com/NixOS/nixpkgs/issues/103746#issuecomment-945091229
  systemd.services."getty@tty1".enable = false;
  systemd.services."autovt@tty1".enable = false;

  # Disable defaults
  programs.nano.enable = false;
  services.xserver.excludePackages = with pkgs; [xterm];
  # Disable documentation desktop shortcut.
  documentation.nixos.enable = false;
  environment.gnome.excludePackages = with pkgs; [
    epiphany
    geary
    gnome-connections
    gnome-contacts
    gnome-maps
    gnome-music
    gnome-photos
    simple-scan
    totem
  ];
  # Shell
  programs.zsh.enable = true;
  users.defaultUserShell = pkgs.zsh;
  programs.command-not-found.enable = true;
  # Git
  programs.git.enable = true;

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
    neovim
    zsh
    git
    wget
    curl
    unzip
    xclip
    gnome-tweaks
    spice
    spice-gtk
    spice-protocol
  ];

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  # Flatpak support.
  services.flatpak.enable = true;
  xdg.portal.enable = true;

  # Make $HOME/.local/bin and $HOME/bin work globally.
  # environment = {
  #   localBinInPath = true;
  #   homeBinInPath = true;
  # };

  # Fonts settings.
  fonts = {
    enableDefaultPackages = true;
    fontDir.enable = true;
    packages = with pkgs; [
      jetbrains-mono
      nerdfonts
      roboto
      roboto-mono
      roboto-serif
      ubuntu_font_family
    ];
  };

  # Gnome-Console settings.
  # console = {
  #   #earlySetup = true;
  #   font = "JetBrainsMonoNerdFont-Regular";
  #   keyMap = "us";
  # };
  # Ghostty # ToDo

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  programs = {
    gnupg.agent = {
      enable = true;
      pinentryPackage = pkgs.pinentry-gnome3;
      enableSSHSupport = true;
    };
  };

  # List services that you want to enable:

  # Enable the OpenSSH daemon.
  # services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "24.11"; # Did you read the comment?

}
