sudo pip3 install python-axolotl
pip3 install Pillow
pip3 install config
pip3 install texttable

/home/shweapi/public_html/trivia.shweapi.com/whatsapp-bot

/opt/trivia/whatsapp-bot


* * * * * /home/shweapi/public_html/trivia.shweapi.com/whatsapp-bot/./start.sh

/home/shweapi/public_html/trivia.shweapi.com/whatsapp-bot/

until /usr/local/bin/python3.5 /home/shweapi/public_html/trivia.shweapi.com/whatsapp-bot/run.py; do
    echo "Whatsapp bot crashed with code $?.  Respawning.." >&2
    sleep 1
done
