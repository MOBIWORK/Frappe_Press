<template>
	<div>
		<header class="sticky top-0 z-10 border-b bg-white px-5 pt-2.5">
			<Breadcrumbs
				:items="[{ label: $t('settings'), route: { name: 'SettingsScreen' } }]"
			/>
			<Tabs :tabs="tabs" class="-mb-px pl-0.5" />
		</header>
		<div class="mx-auto max-w-5xl py-5">
			<router-view />
		</div>
	</div>
</template>

<script>
import Tabs from '@/components/Tabs.vue';

export default {
	name: 'AccountSettings',
	pageMeta() {
		return {
			title: `${this.$t('settings')} - Profile`
		};
	},
	components: {
		Tabs
	},
	computed: {
		tabs() {
			let tabRoute = subRoute => `/settings/${subRoute}`;
			let tabs = [
				{ label: this.$t('profile'), route: 'profile' },
				{
					label: this.$t('team'),
					route: 'team',
					condition: () =>
						$account.user.name === $account.team.user ||
						$account.user.user_type === 'System User'
				}
				// { label: this.$t('developer'), route: 'developer' }
				// { label: 'Đối tác', route: 'partner' }
			].filter(tab => (tab.condition ? tab.condition() : true));

			return tabs.map(tab => {
				return {
					...tab,
					route: tabRoute(tab.route)
				};
			});
		},
		pageSubtitle() {
			const { user, team } = this.$account;
			let subtitle = '';

			if (!user || !team) {
				return subtitle;
			}

			if (team.name !== user.name) {
				if (team.team_title)
					subtitle += `${this.$t('team')}: ${team.team_title}`;
				else subtitle += `${this.$t('team')}: ${team.name}`;
				subtitle += ` &middot; ${this.$t('member')}: ${user.name} `;
			} else {
				subtitle += `<span>${team.name}</span> `;
			}

			if (team.erpnext_partner) {
				subtitle += `&middot; <span>${this.$t(
					'accountsettings_content_1'
				)}</span>`;
			}

			let userTeamMember = team.team_members.filter(
				member => member.user === user.name
			);

			if (userTeamMember.length > 0) {
				userTeamMember = userTeamMember[0];
				const memberSince = this.$date(userTeamMember.creation).toLocaleString({
					month: 'short',
					day: 'numeric',
					year: 'numeric'
				});
				subtitle += `&middot; <span>${this.$t(
					'member_from'
				)} ${memberSince}</span>`;
			}

			return subtitle;
		}
	}
};
</script>
