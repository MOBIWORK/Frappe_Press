<template>
	<div class="text-gray-900 antialiased">
		<div class="flex h-screen overflow-hidden">
			<div
				class="flex flex-1 overflow-y-auto"
				:class="{
					'bg-gray-50':
						$route.meta.isLoginPage && $route.fullPath.indexOf('/checkout') < 0
				}"
			>
				<div class="w-full">
					<Navbar class="md:hidden" v-if="!$route.meta.isLoginPage" />
					<div class="mx-auto flex min-h-full flex-row justify-start">
						<Sidebar
							class="sticky top-0 hidden w-64 flex-shrink-0 md:flex"
							v-if="$auth.isLoggedIn && !$route.meta.hideSidebar"
						/>
						<router-view v-slot="{ Component }" class="w-full sm:mr-0">
							<keep-alive
								:include="[
									// 'Sites',
									'Benches',
									'Servers',
									'Site',
									'Bench',
									'Server',
									// 'Marketplace',
									// 'MarketplaceApp',
									'Account'
								]"
							>
								<component :is="Component" />
							</keep-alive>
						</router-view>
					</div>
				</div>
			</div>
		</div>

		<NotificationToasts />
		<UserPrompts v-if="$auth.isLoggedIn" />
		<ConfirmDialogs />
		<PageLoading />
	</div>
</template>
<script>
import Sidebar from '@/components/Sidebar.vue';
import Navbar from '@/components/Navbar.vue';
import UserPrompts from '@/views/onboarding/UserPrompts.vue';
import ConfirmDialogs from '@/components/ConfirmDialogs.vue';
import NotificationToasts from '@/components/NotificationToasts.vue';
import PageLoading from '@/components/global/PageLoading.vue';

export default {
	name: 'App',
	components: {
		Sidebar,
		Navbar,
		UserPrompts,
		ConfirmDialogs,
		NotificationToasts
	},
	data() {
		return {
			viewportWidth: 0
		};
	},
	provide: {
		viewportWidth: Math.max(
			document.documentElement.clientWidth || 0,
			window.innerWidth || 0
		)
	}
};
</script>
<style src="./assets/style.css"></style>
