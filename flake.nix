{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs = {
    self,
    nixpkgs,
  }: {
    devShell.x86_64-linux = let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in
      pkgs.mkShell {
        buildInputs = with pkgs; [
          python312
          uv
          zsh
        ];

        shellHook = ''
          uv sync --frozen
          source .venv/bin/activate
        '';
      };
  };
}
