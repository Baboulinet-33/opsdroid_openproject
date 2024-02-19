from aiohttp.web import Request, Response

from opsdroid.skill import Skill
from opsdroid.matchers import match_webhook
from opsdroid.events import Message

import logging
import pprint

_LOGGER = logging.getLogger(__name__)

class OpenProject(Skill):
    @match_webhook('webhook')
    async def webhook(self, event: Request):
        """ Define a webhook for OpenProject to Mattermost
        
        Skill parameter:
        - openproject_url: OpenProject URL

        OpenProject action type:
        - work_package:created (the only one implemented)
        - work_package:updated
        - project:created
        - project:updated
        - time_entry:created
        - attachment:created
        """

        payload = await event.json()
        _LOGGER.debug('payload received by openproject webhook: ' + pprint.pformat(payload))
        
        action = payload['action']

        if action != "work_package:created":
            return Response(body="Not implemented", status=501)

        try:
            extracted_values = self.extract_work_package_created_values_from_payload(payload)
            rendered_mattermost = self.render_work_package_created_mattermost(extracted_values)

            await self.opsdroid.send(Message(
                                        target=event.rel_url.query['channel_name'],
                                        text=rendered_mattermost,
                                        connector="mattermost")
                                    )
        except KeyError:
            return Response(body="Error parsing payload", status=500)
        except Exception as e:
            _LOGGER.debug(e)
            return Response(body="Error in webhook OpenProject", status=500)
        
        return Response(body=f"{action}", status=201)

    def extract_work_package_created_values_from_payload(self, payload):
        SUPPORT_URL = self.config['openproject_url']
        link = payload['work_package']['_links']['self']['href']
        link_support = link.replace("/api/v3", SUPPORT_URL)

        extracted_values= {
            'action': "Nouveau ticket",
            'project': payload['work_package']['_embedded']['project']['name'],
            'title': payload['work_package']['subject'],
            'description': payload['work_package']['description']['raw'],
            'link': link_support
        }

        return extracted_values

    def render_work_package_created_mattermost(self, payload):
        render = f"""# [{payload['action']} pour le projet: {payload['project']}]({payload['link']})

**{payload['title']}**
---
{payload['description']}

"""
        return render
