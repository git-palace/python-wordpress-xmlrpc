import xmlrpclib

class WordPressPost(object):
    def __init__(self, xmlrpc=None):
        if xmlrpc:
            self.id = xmlrpc['postid']
            self.user = xmlrpc['userid']
            self.date_created = xmlrpc['dateCreated']
            self.slug = xmlrpc['wp_slug']
            self.post_status = xmlrpc['post_status']
            self.title = xmlrpc['title']
            self.description = xmlrpc['description']
            self.excerpt = xmlrpc['mt_excerpt']
            self.extended_text = xmlrpc['mt_text_more']
            self.link = xmlrpc['link']
            self.permalink = xmlrpc['permaLink']
            self.allow_comments = xmlrpc['mt_allow_comments'] == 1
            self.allow_pings = xmlrpc['mt_allow_pings'] == 1
            self.tags = xmlrpc['mt_keywords']
            self.categories = xmlrpc['categories']
            self.custom_fields = xmlrpc['custom_fields']
        else:
            self.id = None
            self.user = None
            self.date_created = None
            self.slug = ''
            self.post_status = ''
            self.title = ''
            self.description = ''
            self.excerpt = ''
            self.extended_text = ''
            self.link = ''
            self.permalink = ''
            self.allow_comments = False
            self.allow_pings = False
            self.tags = ''
            self.categories = ['Uncategorized']
            self.custom_fields = []

    @property
    def content_struct(self):
        struct = {
            'post_type': 'post',
            'wp_author_id': self.user,
            'title': self.title,
            'description': self.description,
            'mt_excerpt': self.excerpt,
            'mt_text_more': self.extended_text,
            'mt_keywords': self.tags,
            'mt_allow_comments': int(self.allow_comments),
            'mt_allow_pings': int(self.allow_pings),
            'categories': self.categories,
        }

        if self.post_status:
            struct['post_status'] = self.post_status

        if self.date_created:
            struct['dateCreated'] = xmlrpclib.DateTime(self.date_created)

        if self.slug:
            struct['wp_slug'] = self.slug

        if self.custom_fields:
            struct['custom_fields'] = self.custom_fields

        return struct

    def __str__(self):
        return '%s (id=%s)' % (self.slug, self.id)
