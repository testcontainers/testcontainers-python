_poetry_1c0b7ba073df6572_complete()
{
    local cur script coms opts com
    COMPREPLY=()
    _get_comp_words_by_ref -n : cur words

    # for an alias, get the real script behind it
    if [[ $(type -t ${words[0]}) == "alias" ]]; then
        script=$(alias ${words[0]} | sed -E "s/alias ${words[0]}='(.*)'/\1/")
    else
        script=${words[0]}
    fi

    # lookup for command
    for word in ${words[@]:1}; do
        if [[ $word != -* ]]; then
            com=$word
            break
        fi
    done

    # completing for an option
    if [[ ${cur} == --* ]] ; then
        opts="--ansi --directory --help --no-ansi --no-cache --no-interaction --no-plugins --quiet --verbose --version"

        case "$com" in

            (about)
            opts="${opts} "
            ;;

            (add)
            opts="${opts} --allow-prereleases --dev --dry-run --editable --extras --group --lock --optional --platform --python --source"
            ;;

            (build)
            opts="${opts} --format --output"
            ;;

            ('cache clear')
            opts="${opts} --all"
            ;;

            ('cache list')
            opts="${opts} "
            ;;

            (check)
            opts="${opts} --lock"
            ;;

            (config)
            opts="${opts} --list --local --unset"
            ;;

            ('debug info')
            opts="${opts} "
            ;;

            ('debug resolve')
            opts="${opts} --extras --install --python --tree"
            ;;

            ('env info')
            opts="${opts} --executable --path"
            ;;

            ('env list')
            opts="${opts} --full-path"
            ;;

            ('env remove')
            opts="${opts} --all"
            ;;

            ('env use')
            opts="${opts} "
            ;;

            (export)
            opts="${opts} --all-extras --dev --extras --format --only --output --with --with-credentials --without --without-hashes --without-urls"
            ;;

            (help)
            opts="${opts} "
            ;;

            (init)
            opts="${opts} --author --dependency --description --dev-dependency --license --name --python"
            ;;

            (install)
            opts="${opts} --all-extras --compile --dry-run --extras --no-dev --no-directory --no-root --only --only-root --remove-untracked --sync --with --without"
            ;;

            (list)
            opts="${opts} "
            ;;

            (lock)
            opts="${opts} --check --no-update"
            ;;

            (new)
            opts="${opts} --name --readme --src"
            ;;

            (publish)
            opts="${opts} --build --cert --client-cert --dist-dir --dry-run --password --repository --skip-existing --username"
            ;;

            (remove)
            opts="${opts} --dev --dry-run --group --lock"
            ;;

            (run)
            opts="${opts} "
            ;;

            (search)
            opts="${opts} "
            ;;

            ('self add')
            opts="${opts} --allow-prereleases --dry-run --editable --extras --source"
            ;;

            ('self install')
            opts="${opts} --dry-run --sync"
            ;;

            ('self lock')
            opts="${opts} --check --no-update"
            ;;

            ('self remove')
            opts="${opts} --dry-run"
            ;;

            ('self show')
            opts="${opts} --addons --latest --outdated --tree"
            ;;

            ('self show plugins')
            opts="${opts} "
            ;;

            ('self update')
            opts="${opts} --dry-run --preview"
            ;;

            (shell)
            opts="${opts} "
            ;;

            (show)
            opts="${opts} --all --latest --no-dev --only --outdated --top-level --tree --why --with --without"
            ;;

            ('source add')
            opts="${opts} --default --priority --secondary"
            ;;

            ('source remove')
            opts="${opts} "
            ;;

            ('source show')
            opts="${opts} "
            ;;

            (update)
            opts="${opts} --dry-run --lock --no-dev --only --sync --with --without"
            ;;

            (version)
            opts="${opts} --dry-run --next-phase --short"
            ;;

        esac

        COMPREPLY=($(compgen -W "${opts}" -- ${cur}))
        __ltrim_colon_completions "$cur"

        return 0;
    fi

    # completing for a command
    if [[ $cur == $com ]]; then
        coms="about add build 'cache clear' 'cache list' check config 'debug info' 'debug resolve' 'env info' 'env list' 'env remove' 'env use' export help init install list lock new publish remove run search 'self add' 'self install' 'self lock' 'self remove' 'self show' 'self show plugins' 'self update' shell show 'source add' 'source remove' 'source show' update version"

        COMPREPLY=($(compgen -W "${coms}" -- ${cur}))
        __ltrim_colon_completions "$cur"

        return 0
    fi
}

complete -o default -F _poetry_1c0b7ba073df6572_complete poetry
complete -o default -F _poetry_1c0b7ba073df6572_complete /home/bstrausser/.local/share/pypoetry/venv/bin/poetry
