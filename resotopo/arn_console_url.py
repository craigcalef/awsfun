class ARN:
    def __init__(self, text):
        text = text.strip()

        # split into tokens; leaving resource-id with colons together
        first_tokens = text.split(':')
        tokens = first_tokens[:6]
        if len(first_tokens) > 6:
            tokens.append(':'.join(first_tokens[6:]))

        # arn:partition:service:region:account-id:...
        self.prefix = tokens[0]
        self.partition = tokens[1]
        self.service = tokens[2]
        self.region = tokens[3]
        self.account = tokens[4]
        self.resource_revision = ''

        # ...:resource-type:resource-id (resource-id can contain colons!)
        if len(tokens) >= 7:
            if '/' in tokens[5]:
                self.resource_type = tokens[5].split('/')[0]
                self.resource = '/'.join(tokens[5].split('/')[1:])
                self.resource_revision = tokens[6]
                self.has_path = True
            else:
                self.resource_type = tokens[5]
                self.resource = tokens[6]
                self.has_path = False

        # ...:resource-type/resource-id (resource-id can contain slashes!)
        elif '/' in tokens[5]:
            self.resource_type = tokens[5].split('/')[0]
            self.resource = '/'.join(tokens[5].split('/')[1:])
            self.has_path = True

        # ...:resource-id
        elif tokens[5]:
            self.resource_type = ''
            self.resource = tokens[5]
            self.has_path = False

        # anything else
        else:
            raise ValueError("Bad number of tokens")

        self._link_templates = self._get_link_templates()

    @property
    def string(self):
        if not self.resource_type:
            return f"{self.prefix}:{self.partition}:{self.service}:{self.region}:{self.account}:{self.resource}"
        elif self.has_path:
            if self.resource_revision:
                return f"{self.prefix}:{self.partition}:{self.service}:{self.region}:{self.account}:{self.resource_type}/{self.resource}:{self.resource_revision}"
            else:
                return f"{self.prefix}:{self.partition}:{self.service}:{self.region}:{self.account}:{self.resource_type}/{self.resource}"
        else:
            return f"{self.prefix}:{self.partition}:{self.service}:{self.region}:{self.account}:{self.resource_type}:{self.resource}"

    @property
    def console(self):
        if self.partition == "aws":
            return "console.aws.amazon.com"
        elif self.partition == "aws-us-gov":
            return "console.amazonaws-us-gov.com"
        elif self.partition == "aws-cn":
            return "console.amazonaws.cn"
        else:
            raise ValueError(f"Bad/unsupported AWS partition: {self.partition}")

    @property
    def qualifiers(self):
        return self.resource.split(':')

    @property
    def path_all_but_last(self):
        # Example: "aws-service-role/support.amazonaws.com/AWSServiceRoleForSupport" -> "aws-service-role/support.amazonaws.com"
        return self.resource[:self.resource.rfind('/')]

    @property
    def path_last(self):
        # Example: "aws-service-role/support.amazonaws.com/AWSServiceRoleForSupport" -> "AWSServiceRoleForSupport"
        return self.resource[self.resource.rfind('/') + 1:]

    @property
    def console_link(self):
        if self.prefix != "arn":
            raise ValueError(f"Bad ARN prefix {self.prefix}")

        service_console_link_templates = self._link_templates[self.service]
        if service_console_link_templates is None:
            raise ValueError(f"AWS service {self.service} unknown")

        template = service_console_link_templates.get(self.resource_type)
        if not template:
            raise ValueError(f"AWS service {self.service} resource type {self.resource_type} not supported")

        return template(self)

    def _get_link_templates(self):
        # Implementation of _get_link_templates goes here
        pass