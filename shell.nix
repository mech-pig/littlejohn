let
  nixpkgs = builtins.fetchGit {
    name = "nixos-unstable-2021-03-02";
    url = "https://github.com/NixOS/nixpkgs/";
    ref = "refs/heads/nixos-unstable";
    rev = "0aeba64fb26e4defa0842a942757144659c6e29f";
  };

  pkgs = import nixpkgs {};
in
  pkgs.mkShell {
    buildInputs = [
      pkgs.poetry
      pkgs.python39
    ];
  }