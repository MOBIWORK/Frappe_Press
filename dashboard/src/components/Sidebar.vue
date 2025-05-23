<template>
	<div class="flex h-screen flex-col justify-between bg-gray-50 p-2">
		<div>
			<Dropdown :options="dropdownItems">
				<template v-slot="{ open }">
					<button
						class="flex w-[15rem] items-center rounded-md px-2 py-2 text-left"
						:class="open ? 'bg-white shadow-sm' : 'hover:bg-gray-200'"
					>
						<FCLogo class="h-8 w-8 rounded" />
						<div class="ml-2 flex flex-col">
							<div class="text-base font-medium leading-none text-gray-900">
								MBWCloud
							</div>
							<div
								v-if="$account.user"
								class="mt-1 hidden text-sm leading-none text-gray-700 sm:inline"
							>
								{{ $account.user.full_name }}
							</div>
						</div>
						<FeatherIcon
							name="chevron-down"
							class="ml-auto h-5 w-5 text-gray-700"
						/>
					</button>
				</template>
			</Dropdown>
			<div class="mt-2 flex flex-col space-y-0.5">
				<div class="mb-2 flex flex-col space-y-0.5">
					<button
						v-if="$account.number_of_sites > 3"
						class="rounded text-gray-900 hover:bg-gray-100"
						@click="show = true"
					>
						<div class="flex w-full items-center px-2 py-1">
							<span class="mr-1.5">
								<FeatherIcon name="search" class="h-5 w-5 text-gray-700" />
							</span>
							<span class="text-sm">{{ $t('search') }}</span>
							<span class="ml-auto text-sm text-gray-500">
								<template v-if="$platform === 'mac'">⌘K</template>
								<template v-else>Ctrl+K</template>
							</span>
						</div>
					</button>
					<button
						class="rounded text-gray-900 hover:bg-gray-100"
						@click="this.$router.push({ name: 'Notifications' })"
					>
						<div
							class="flex w-full items-center rounded-md px-2 py-1"
							:class="{
								'bg-white shadow-sm':
									this.$route.fullPath.startsWith('/notifications')
							}"
						>
							<span class="mr-1.5">
								<FeatherIcon name="inbox" class="h-4.5 w-4.5 text-gray-700" />
							</span>
							<span class="text-sm"> {{ $t('notifications') }} </span>
							<span
								v-if="unreadNotificationsCount > 0"
								class="ml-auto rounded bg-gray-400 px-1.5 py-0.5 text-xs text-white"
							>
								{{
									unreadNotificationsCount > 99
										? '99+'
										: unreadNotificationsCount
								}}
							</span>
						</div>
					</button>
				</div>
				<CommandPalette
					:show="showCommandPalette"
					@close="showCommandPalette = false"
				/>
				<router-link
					v-for="item in items"
					:key="item.label"
					:to="item.route"
					v-slot="{ href, route, navigate }"
				>
					<a
						:class="[
							(
								Boolean(item.highlight)
									? item.highlight(route)
									: item.route == '/'
							)
								? 'bg-white shadow-sm'
								: 'text-gray-900 hover:bg-gray-100'
						]"
						:href="href"
						@click="navigate"
						class="flex items-center rounded-md px-2 py-1 pr-10 text-start text-sm focus:outline-none"
					>
						<Component class="mr-1.5 text-gray-700" :is="item.icon" />
						{{ item.label }}
					</a>
				</router-link>
			</div>
		</div>
		<SwitchTeamDialog v-model="showTeamSwitcher" />
		<SwitchLangDialog v-model="showLangSwitcher" />
	</div>
</template>

<script>
import { FCIcons } from '@/components/icons';
import SwitchTeamDialog from './SwitchTeamDialog.vue';
import SwitchLangDialog from './SwitchLangDialog.vue';
import FCLogo from '@/components/icons/FCLogo.vue';
import CommandPalette from '@/components/CommandPalette.vue';
import { unreadNotificationsCount } from '@/data/notifications';
import { showLanguage, setShowLanguage } from '@/composables/language';
import { watch } from 'vue';

export default {
	name: 'Sidebar',
	components: {
		FCLogo,
		SwitchTeamDialog,
		CommandPalette,
		SwitchLangDialog
	},
	created() {
		// Watch biến ref ngoài component
		watch(showLanguage, val => {
			this.showLangSwitcher = val;
		});
	},
	watch: {
		'$i18n.locale'() {
			this.dropdownItems = this.getValueMenu();
		}
	},
	data() {
		return {
			showCommandPalette: false,
			showTeamSwitcher: false,
			showLangSwitcher: showLanguage.value,
			dropdownItems: this.getValueMenu()
		};
	},
	mounted() {
		window.addEventListener('keydown', e => {
			if (e.key === 'k' && (e.ctrlKey || e.metaKey)) {
				this.showCommandPalette = !this.showCommandPalette;
				e.preventDefault();
			}
			if (e.key === 'Escape') {
				this.showCommandPalette = false;
			}
		});

		this.$socket.on('press_notification', data => {
			if (data.team === this.$account.team.name) {
				unreadNotificationsCount.setData(data => data + 1);
			}
		});

		unreadNotificationsCount.fetch();
	},
	computed: {
		unreadNotificationsCount() {
			return unreadNotificationsCount.data;
		},
		items() {
			return [
				{
					label: this.$t('sites'),
					route: '/sites',
					highlight: () => {
						return this.$route.fullPath.startsWith('/sites');
					},
					icon: FCIcons.SiteIcon
				},
				{
					label: 'Benches',
					route: '/benches',
					highlight: () => {
						return this.$route.fullPath.startsWith('/benches');
					},
					icon: FCIcons.BenchIcon,
					condition: () => this.$account.team?.benches_enabled
				},
				{
					label: 'Servers',
					route: '/servers',
					highlight: () => {
						return this.$route.fullPath.startsWith('/servers');
					},
					icon: FCIcons.ServerIcon,
					condition: () => this.$account.team?.servers_enabled
				},
				{
					label: 'Spaces',
					route: '/spaces',
					highlight: () => {
						return this.$route.fullPath.startsWith('/spaces');
					},
					icon: FCIcons.SpacesIcon,
					condition: () => this.$account.team?.code_servers_enabled
				},
				{
					label: this.$t('apps'),
					route: '/marketplace/apps',
					highlight: () => {
						return this.$route.fullPath.startsWith('/marketplace');
					},
					icon: FCIcons.AppsIcon,
					condition: () => this.$account.team?.is_developer
				},
				{
					label: this.$t('security'),
					route: '/security',
					highlight: () => {
						return this.$route.fullPath.startsWith('/security');
					},
					icon: FCIcons.SecurityIcon,
					condition: () => this.$account.team?.security_portal_enabled
				},
				{
					label: this.$t('billing'),
					route: '/billing',
					highlight: () => {
						return this.$route.fullPath.startsWith('/billing');
					},
					icon: FCIcons.BillingIcon,
					condition: () =>
						$account.user?.name === $account.team?.user ||
						$account.user?.user_type === 'System User'
				},
				{
					label: this.$t('settings'),
					route: '/settings',
					highlight: () => {
						return this.$route.fullPath.startsWith('/settings');
					},
					icon: FCIcons.SettingsIcon
				}
			].filter(d => (d.condition ? d.condition() : true));
		}
	},
	methods: {
		getValueMenu() {
			return [
				{
					label: this.$t('switch_team'),
					icon: 'command',
					onClick: () => (this.showTeamSwitcher = true)
				},
				{
					label: this.$t('support_and_docs'),
					icon: 'help-circle',
					onClick: () => (window.location.href = 'https://mbw.vn')
				},
				{
					label: this.$t('settings'),
					icon: 'settings',
					onClick: () => this.$router.push('/settings/profile')
				},
				{
					label: this.$t('language'),
					icon: 'globe',
					onClick: () => {
						setShowLanguage(true);
					}
				},
				{
					label: this.$t('logout'),
					icon: 'log-out',
					onClick: () => this.$auth.logout()
				}
			];
		}
	}
};
</script>
