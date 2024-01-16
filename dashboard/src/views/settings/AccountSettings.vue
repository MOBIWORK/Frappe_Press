<template>
	<div>
		<header class="sticky top-0 border-b bg-white px-5 pt-2.5">
			<Breadcrumbs
				:items="[{ label: 'Cài đặt', route: { name: 'SettingsScreen' } }]"
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
			title: 'Settings - Profile'
		};
	},
	components: {
		Tabs
	},
	computed: {
		tabs() {
			let tabRoute = subRoute => `/settings/${subRoute}`;
			let tabs = [
				{ label: 'Hồ sơ', route: 'profile' },
				{
					label: 'Nhóm',
					route: 'team',
					condition: () =>
						$account.user.name === $account.team.user ||
						$account.user.user_type === 'System User'
				},
				{ label: 'Phát triển', route: 'developer' }
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
				if (team.team_title) subtitle += `Nhóm: ${team.team_title}`;
				else subtitle += `Nhóm: ${team.name}`;
				subtitle += ` &middot; Thành viên: ${user.name} `;
			} else {
				subtitle += `<span>${team.name}</span> `;
			}

			if (team.erpnext_partner) {
				subtitle += `&middot; <span>ERPNext Đối tác</span>`;
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
				subtitle += `&middot; <span>Thành viên từ ${memberSince}</span>`;
			}

			return subtitle;
		}
	}
};
</script>
