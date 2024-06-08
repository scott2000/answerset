{
  description = ''
    Anki add-on for multiple answers in "type in the answer" cards
  '';

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonWithPackages = pkgs.python311.withPackages (
          python-pkgs: with python-pkgs; [
            mypy
            pytest
            pytest-cov
          ]
        );

        packages = with pkgs; [
          anki
          pythonWithPackages
          ruff
          zip
        ];
      in
      {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "answerset";
          version = self.shortRev or "dirty";
          src = self;
          nativeBuildInputs = packages;
          doCheck = true;
          checkTarget = "test";
          installPhase = ''
            mkdir $out
            cp answerset.ankiaddon $out
          '';
        };

        checks.default = self.packages.${system}.default;

        devShells.default = pkgs.mkShell { inherit packages; };

        formatter = pkgs.nixfmt-rfc-style;
      }
    );
}
