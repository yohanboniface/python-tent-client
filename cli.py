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
    def __init__(self, *args, **kwargs):
        print yellow('-' * 80)

        self.app = tentapp.TentApp()
        self.app.authorizeFromCommandLine()

    def print_post(self, post):
        if post['type'] == 'https://tent.io/types/post/status/v0.1.0':
            timestamp = time.asctime(time.localtime(post['published_at']))
            print '%s    %s' % (yellow(post['entity']), white(timestamp))
            print '    %s' % cyan(post['content']['text'])
            print

    def handle_command(self, command):
        command = command[1:]
        if command in ("update", "up"):
            posts = self.app.getPosts()

            # # By default posts are sorted newest first.
            if self.app.config.get("UI", "sort") == "desc":
                posts.sort(key=lambda p: p['published_at'])

            for post in posts:
                self.print_post(post)
        elif command == "profile":
            print yellow('PROFILE:')
            profile = self.app.getProfile()
            debugJson(profile)
        elif command == "followings":
            print yellow('FOLLOWINGS:')
            followings = self.app.getFollowings()
            debugJson(followings)
        elif command == "followers":
            print yellow('FOLLOWERS:')
            followers = self.app.getFollowers()
            debugJson(followers)
        elif command == "status":
            status = raw_input('Type your post:\n')
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
        elif command in ("help", "h"):
            print """
            Available commands:
            /update, /up    => update the feed
            /status         => post a status
            /profile        => get your profile infos
            /followers      => get your followers list
            /followings     => get your followings list
            /help, /h       => display this help message and reprompt
            """

    def __call__(self):
        while 1:
            try:
                command = raw_input("(Type /h for help)\n[%s] " % self.app.entityUrl)
                self.handle_command(command)
            except KeyboardInterrupt:
                print "\nExciting, bye!\n"
                break
            print yellow('-' * 80)
