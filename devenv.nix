{ pkgs, lib, config, inputs, ... }:
let
  USE_HOST_NET = 1;
  USE_NIX = 0;
in
{
  # https://devenv.sh/basics/
  env = {
    GREET = "BS INT";
    DOCKER_COMPOSE_EXECUTABLE = "docker compose";
    PROD_COMPOSE_ARGS = "-f docker-compose.yml -f docker-compose.prod.yml";
    DEV_COMPOSE_ARGS = let
      nix-config = if USE_NIX == 1
      then "-f docker-compose.nix.yml"
      else "";
      host-config = if USE_HOST_NET == 1
      then "-f docker-compose.host.yml"
      else "";
    in "-f docker-compose.yml -f docker-compose.dev.yml ${nix-config} ${host-config}";
  };

  # https://devenv.sh/packages/
  packages = [ pkgs.gnumake ];

  # https://devenv.sh/languages/
  languages = {
    python = {
      enable = true;
      version = "3.12";
      uv = {
        enable = true;
        sync.enable = true;
      };
    };
  };

  # https://devenv.sh/processes/
  # processes.cargo-watch.exec = "cargo-watch";

  # https://devenv.sh/services/
  # services.postgres.enable = true;

  # https://devenv.sh/scripts/
  scripts = {
    build.exec = ''
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS build bs_int
    '';
    init.exec = ''
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS down -v --remove-orphans
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS up -d postgres
      sleep 3
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS run --rm bs_int /venv/bin/bs-int migrate
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS run --rm bs_int /venv/bin/bs-int initdata
    '';
    attach.exec = ''
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS up -d
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS attach bs_int
    '';
    up.exec = ''
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS up -d
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS logs -f bs_int
    '';
    down.exec = ''
      $DOCKER_COMPOSE_EXECUTABLE $DEV_COMPOSE_ARGS down --remove-orphans
    '';
    hello.exec = ''
      echo Welcome to $GREET
    '';
  };

  enterShell = ''
    hello
  '';

  # https://devenv.sh/tasks/
  # tasks = {
  #   "myproj:setup".exec = "mytool build";
  #   "devenv:enterShell".after = [ "myproj:setup" ];
  # };

  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    make tests
  '';

  # https://devenv.sh/git-hooks/
  git-hooks.hooks = {
    ruff.enable = true;
    ruff-format.enable = true;
  };

  # See full reference at https://devenv.sh/reference/options/
}
