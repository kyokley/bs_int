{ pkgs, lib, config, inputs, ... }:
let
  USE_HOST_NET = 1;
in
{
  # https://devenv.sh/basics/
  env = {
    GREET = "BS INT";
    DOCKER_COMPOSE_EXECUTABLE = "docker compose";
    PROD_COMPOSE_ARGS = "-f docker-compose.yml -f docker-compose.prod.yml";
    DEV_COMPOSE_ARGS = "-f docker-compose.yml -f docker-compose.dev.yml";
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
    build.exec = let
      host =
        if USE_HOST_NET == 1
        then "--network=host"
        else "";
    in "docker build ${host} --tag=kyokley/bs_int .";
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
