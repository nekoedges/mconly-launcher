{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    # Pythom
    python314
    python314Packages.requests python314Packages.tqdm
    # Libs
    glibc
    libX11 libXext libXcursor libXrandr libXxf86vm libGL
    libXau libXdmcp libXrender libXfixes libxcb mesa
    font-manager
    # Java
    (zulu8.override {enableJavaFX = true;})
  ];

  shellHook = ''
    # Some of my NixOS packages is breaking LD_LIBRARY_PATH, so it's a fix, but I hate it
    export LD_LIBRARY_PATH="${pkgs.libX11}/lib:${pkgs.libXext}/lib:${pkgs.libXcursor}/lib:${pkgs.libXrandr}/lib:${pkgs.libXxf86vm}/lib:${pkgs.libGL}/lib:${pkgs.libxcb}/lib:${pkgs.mesa}/lib:${pkgs.font-manager}/lib:$LD_LIBRARY_PATH"
    echo "Shell is ready, download minecraft and run it"
  '';
}
