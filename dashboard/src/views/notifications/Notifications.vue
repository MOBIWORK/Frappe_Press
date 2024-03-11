<template>
	<div>
		<header
			class="sticky top-0 z-10 flex items-center justify-between border-b bg-white px-5 py-2.5"
		>
			<Breadcrumbs
				:items="[
					{ label: $t('notifications'), route: { name: 'Notifications' } }
				]"
			>
				<template #actions>
					<TabButtons
						:buttons="[
							{ label: $t('Unread'), value: 'unread', active: true },
							{ label: $t('Read'), value: 'read' }
						]"
						v-model="activeTab"
					/>
				</template>
			</Breadcrumbs>
		</header>

		<div class="mx-20 mt-5">
			<div class="flex flex-col divide-y">
				<ListItem
					v-for="notification in notifications"
					:title="notification.type"
					:description="`${notification.message} • ${formatDate(
						notification.creation,
						'relative'
					)}`"
				>
					<template #actions>
						<Button
							variant="ghost"
							:label="$t('view')"
							@click="openNotification(notification)"
						/>
					</template>
				</ListItem>
				<div v-if="!notifications?.length" class="text-base text-gray-600">
					{{ $t('no_notifications') }}
				</div>
			</div>
		</div>
	</div>
</template>

<script>
import { TabButtons } from 'frappe-ui';
import { unreadNotificationsCount } from '@/data/notifications';

export default {
	name: 'Notifications',
	pageMeta() {
		return {
			title: this.$t('notifications')
		};
	},
	components: {
		TabButtons
	},
	data() {
		return {
			activeTab: 'unread'
		};
	},
	resources: {
		unreadNotifications() {
			if (this.activeTab !== 'unread') return;
			return {
				url: 'press.api.notifications.get_notifications',
				params: {
					filters: { team: this.$account.team.name, read: false }
				},
				cache: ['unreadNotifications', this.$account?.team],
				auto: true
			};
		},
		readNotifications() {
			if (this.activeTab !== 'read') return;
			return {
				url: 'press.api.notifications.get_notifications',
				params: {
					filters: {
						team: this.$account.team.name,
						read: true
					}
				},
				cache: ['readNotifications', this.$account?.team],
				auto: true
			};
		},
		markNotificationAsRead: {
			url: 'press.api.notifications.mark_notification_as_read'
		}
	},
	methods: {
		openNotification(notification) {
			if (!notification.read) {
				this.$resources.markNotificationAsRead.submit({
					name: notification.name
				});

				unreadNotificationsCount.setData(data => data - 1);
			}
			this.$router.push(notification.route);
		}
	},
	computed: {
		notifications() {
			return this.activeTab === 'unread'
				? this.$resources.unreadNotifications.data
				: this.$resources.readNotifications.data;
		}
	}
};
</script>
