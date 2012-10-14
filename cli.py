from __future__ import division
import time
import tentapp
import readline

from colors import *
from utils import debugJson


class Cli(object):
    """
    Tent command line manager.
    """

    COMMANDS = [
        "update",
        "help",
        "profile",
        "followers",
        "followings",
        "status",
    ]

    def __init__(self, *args, **kwargs):
        print yellow('-' * 80)
        print yellow('LOADING...')

        self.app = tentapp.TentApp()
        self.app.authorizeFromCommandLine()
        readline.set_completer(self.completer)
        readline.parse_and_bind("tab: complete")
        print yellow('-' * 80)

    def print_post(self, post):
        if post['type'] == 'https://tent.io/types/post/status/v0.1.0':
            timestamp = time.asctime(time.localtime(post['published_at']))
            print '%s    %s' % (yellow(post['entity']), white(timestamp))
            print '    %s' % cyan(post['content']['text'])
            print

    def completer(self, text, state):
        if not text:
            return
        # TODO: implement following completion while writing status.
        for cmd in self.COMMANDS:
            if cmd.startswith(text):
                if not state:
                    return cmd
                else:
                    state -= 1

    def do_help(self, *args, **kwargs):
        print """
        Available commands:
        /update, /up    => update the feed
        /status         => post a status
        /profile        => get your profile infos
        /followers      => get your followers list
        /followings     => get your followings list
        /help, /h       => display this help message and reprompt
        """

    def do_h(self, *args, **kwargs):
        self.do_help(*args, **kwargs)

    def do_up(self, *args, **kwargs):
        self.do_update(*args, **kwargs)

    def do_update(self, *args, **kwargs):
        posts = self.app.getPosts()

        # By default posts are sorted newest first.
        if self.app.config.get("UI", "sort") == "desc":
            posts.sort(key=lambda p: p['published_at'])

        for post in posts:
            self.print_post(post)

    def do_profile(self, *args, **kwargs):
        print yellow('PROFILE:')
        profile = self.app.getProfile()
        debugJson(profile)

    def do_followings(self, *args, **kwargs):
        print yellow('FOLLOWINGS:')
        followings = self.app.getFollowings()
        debugJson(followings)

    def do_followers(self, *args, **kwargs):
        print yellow('FOLLOWERS:')
        followers = self.app.getFollowers()
        debugJson(followers)

    def do_status(self, *args, **kwargs):
        try:
            status = raw_input('Type your post:\n')
        except KeyboardInterrupt:
            print red("Status cancelled.")
            pass
        else:
            post = {
                'type': 'https://tent.io/types/post/status/v0.1.0',
                'published_at': int(time.time()),
                'permissions': {
                    'public': True,
                },
                'licenses': ['http://creativecommons.org/licenses/by/3.0/'],
                'content': {
                    'text': status,
                }
            }
            self.app.putPost(post)

    def handle_command(self, command):
        command = command[1:]
        fx_name = 'do_%s' % command
        if hasattr(self, fx_name):
            return getattr(self, fx_name)()
        else:
            print red('No command with name %s' % command)

    def __call__(self):
        while 1:
            try:
                command = raw_input("(Type /h for help)\n[%s] " % self.app.entityUrl)
                self.handle_command(command)
            except KeyboardInterrupt:
                print "\nExciting, bye!\n"
                break
            print yellow('-' * 80)
