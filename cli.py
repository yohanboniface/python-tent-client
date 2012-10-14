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
        self._posts = []  # TODO: store and reload posts
        self.do_GET_help()
        print yellow('-' * 80)

    def print_post(self, post, idx=None):
        if post['type'] == 'https://tent.io/types/post/status/v0.1.0':
            timestamp = time.asctime(time.localtime(post['published_at']))
            local_id = white("%d " % idx) if idx else ""
            print '%s%s    %s' % (local_id, yellow(post['entity']), white(timestamp))
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

    def do_GET_help(self, *args, **kwargs):
        print """
        Available commands:
        GET posts           => get your feed
        GET posts <id>      => get details of post with id <id>
        POST posts <type>   => POST a post of type <type>
        GET profile         => get your profile infos
        GET followers       => get your followers list
        GET followings      => get your followings list
        GET help            => display this help message and reprompt

        Note: "GET" is the default verb and can always be ommited.
        """

    def do_GET_profile(self, *args, **kwargs):
        print yellow('PROFILE:')
        profile = self.app.getProfile()
        debugJson(profile)

    def do_GET_followings(self, *args, **kwargs):
        print yellow('FOLLOWINGS:')
        followings = self.app.getFollowings()
        debugJson(followings)

    def do_GET_followers(self, *args, **kwargs):
        print yellow('FOLLOWERS:')
        followers = self.app.getFollowers()
        debugJson(followers)

    def do_GET_posts_detail(self, idx, *args):
        # Only working for personal posts currently (GET url must be
        # changed on the fly to fix this)
        post_id = self._posts[idx]['id']
        post = self.app.getPosts(id=post_id)
        self.print_post(post)

    def do_GET_posts(self, *args, **kwargs):
        if len(args) > 0:
            try:
                idx = int(args[0])  # this is the local index of the post
                self.do_GET_posts_detail(idx)
            except ValueError:
                print red('Arguments %s not understood' % args)
                pass
        else:
            self._posts = self.app.getPosts()

            # By default posts are sorted newest first.
            if self.app.config.get("UI", "sort") == "desc":
                self._posts.sort(key=lambda p: p['published_at'])

            for idx, post in enumerate(self._posts):
                self.print_post(post, idx)

    def do_POST_posts(self, post_type, *args, **kwargs):
        valid_types = ['status']
        if not post_type in valid_types:
            print red(u"%s is not a valid post type" % post_type)
            return
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

    def handle_command(self, command_line):
        if not command_line:
            return
        command_args = command_line.split(' ')
        if not command_line[0].isupper():
            verb = "GET"  # default verb
            command = command_args.pop(0)
        else:
            verb = command_args.pop(0)
            if not verb in ['POST', 'GET']:  # TODO: make it action relative
                return red('Verb %s not understood' % verb)
            try:
                command = command_args.pop(0)
            except IndexError:
                return red('Missing command')
        fx_name = 'do_%s_%s' % (verb, command)
        if hasattr(self, fx_name):
            return getattr(self, fx_name)(*command_args)
        else:
            print red('No command with verb %s and name %s' % (verb, command))

    @property
    def intro(self):
        """
        Return text displayed before prompt cursor.
        """
        return self.app.entityUrl.split('//')[-1]

    def prompt(self):
        command = raw_input("[%s] " % self.intro)
        return command

    def __call__(self):
        while 1:
            try:
                command = self.prompt()
                self.handle_command(command)
            except KeyboardInterrupt:
                print "\nExciting, bye!\n"
                break
            print yellow('-' * 80)
