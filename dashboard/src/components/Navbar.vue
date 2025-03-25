<template>
	<nav class="border-b bg-gray-50 px-4">
		<div class="z-10 mx-auto md:container">
			<div class="flex h-16 items-center justify-between">
				<div class="flex items-center">
					<div class="shrink-0">
						<router-link to="/">
							<FrappeCloudLogo class="h-8" />
						</router-link>
					</div>
				</div>
				<div class="-mr-2 flex md:hidden">
					<button
						class="focus:shadow-outline-gray inline-flex items-center justify-center rounded-md p-2 text-gray-700 focus:outline-none"
						@click="mobileMenuOpen = !mobileMenuOpen"
					>
						<FeatherIcon v-if="!mobileMenuOpen" name="menu" class="h-6 w-6" />
						<FeatherIcon v-else name="x" class="h-6 w-6" />
					</button>
				</div>
			</div>
		</div>
		<div class="md:hidden" :class="mobileMenuOpen ? 'block' : 'hidden'">
			<div class="px-4 pb-2">
				<router-link
					v-for="item in items"
					:key="item.label"
					:to="item.route"
					v-slot="{ href, route, navigate, isActive, isExactActive }"
				>
					<a
						:class="[
							(
								Boolean(item.highlight)
									? item.highlight(route)
									: item.route == '/'
							)
								? 'bg-gray-200'
								: 'text-gray-900 hover:bg-gray-50'
							// (item.route == '/' ? isExactActive : isActive)
							// 	? 'bg-gray-200'
							// 	: 'text-gray-900 hover:bg-gray-50'
						]"
						:href="href"
						@click="navigate"
						class="block rounded-md px-3 py-2 text-sm font-medium focus:outline-none"
					>
						{{ item.label }}
					</a>
				</router-link>
			</div>
			<div class="border-t pb-3 pt-4">
				<div class="flex items-center px-4">
					<div class="shrink-0">
						<Avatar
							v-if="$account.user"
							:label="$account.user.first_name"
							:image="$account.user.user_image"
						/>
					</div>
					<div class="ml-3" v-if="$account.user">
						<div class="text-base font-medium leading-none">
							{{ $account.user.first_name }} {{ $account.user.last_name }}
						</div>
						<div class="mt-1 text-sm font-medium leading-none text-gray-400">
							{{ $account.user.email }}
						</div>
					</div>
				</div>
				<div class="mt-3 space-y-3 px-2">
					<a
						href="https://support.eov.solutions"
						target="_blank"
						class="block rounded-md px-3 pt-4 text-base font-medium focus:outline-none"
					>
						{{ $t('support_and_docs') }}
					</a>
					<button
						class="block rounded-md px-3 text-base font-medium focus:outline-none"
						@click="this.showLangSwitcher = true"
					>
						{{ $t('language') }}
					</button>
					<a
						href="#"
						class="block rounded-md px-3 text-base font-medium focus:outline-none"
						@click.prevent="$auth.logout"
					>
						{{ $t('logout') }}
					</a>
				</div>
			</div>
		</div>
		<SwitchLangDialog v-model="showLangSwitcher" />
	</nav>
</template>

<script>
import FrappeCloudLogo from '@/components/icons/FrappeCloudLogo.vue';
import SwitchLangDialog from './SwitchLangDialog.vue';

export default {
	components: {
		FrappeCloudLogo,
		SwitchLangDialog
	},
	data() {
		return {
			showLangSwitcher: false,
			mobileMenuOpen: false
		};
	},
	computed: {
		items() {
			return [
				{
					label: this.$t('sites'),
					route: '/sites',
					highlight: () => {
						return this.$route.fullPath.endsWith('/sites');
					}
				},
				{
					label: 'Benches',
					route: '/benches',
					highlight: () => {
						return this.$route.fullPath.endsWith('/benches');
					},
					condition: () => this.$account.team?.benches_enabled
				},
				{
					label: this.$t('apps'),
					route: '/marketplace/apps',
					highlight: () => {
						return this.$route.fullPath.includes('/marketplace/');
					},
					condition: () => this.$account.team?.is_developer
				},
				{
					label: this.$t('billing'),
					route: '/billing',
					highlight: () => {
						return this.$route.fullPath.includes('/billing/');
					}
				},
				{
					label: this.$t('settings'),
					route: '/settings/profile',
					highlight: () => {
						return this.$route.fullPath.includes('/settings');
					}
				}
			].filter(d => (d.condition ? d.condition() : true));
		}
	}
};
</script>
