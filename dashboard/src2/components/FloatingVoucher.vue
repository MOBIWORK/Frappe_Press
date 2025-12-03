<template>
	<div v-if="vouchers.length > 0" class="fixed bottom-4 right-4 sm:bottom-5 sm:right-5 md:bottom-6 md:right-6 lg:bottom-8 lg:right-8 z-50">
		<!-- Stacking Voucher Cards -->
		<Transition name="voucher-panel">
			<div v-if="showPanel" class="voucher-panel absolute bottom-12 p-3 sm:bottom-12 md:bottom-14 right-0 w-[280px] sm:w-80 md:w-[340px] lg:w-[360px] max-h-[50vh] sm:max-h-[55vh] md:max-h-[60vh] overflow-y-auto rounded-xl">
				<!-- Close button -->
				<button 
					@click="showPanel = false"
					class="sticky top-0 float-right -mr-1 -mt-1 z-10 w-6 h-6 bg-white rounded-full shadow-md flex items-center justify-center text-gray-400 hover:text-gray-600 transition-colors"
				>
					<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
					</svg>
				</button>
				
				<!-- Voucher Cards Stack -->
				<div class="relative p-2 sm:p-3">
					<TransitionGroup name="stack-card">
						<div
							v-for="(voucher, index) in vouchers"
							:key="voucher.code"
							class="voucher-card bg-white border border-blue-100 rounded-lg sm:rounded-xl p-2.5 sm:p-3 md:p-4 shadow-md hover:shadow-lg mb-2 sm:mb-2.5 md:mb-3"
							:style="{
								zIndex: vouchers.length - index
							}"
						>
							<div class="flex items-start gap-2 sm:gap-2.5 md:gap-3">
								<!-- Voucher Icon -->
								<div class="flex-shrink-0 w-8 h-8 sm:w-9 sm:h-9 md:w-10 md:h-10 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center">
									<svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 sm:h-4.5 sm:w-4.5 md:h-5 md:w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
									</svg>
								</div>
								<div class="flex-1 min-w-0">
									<h3 class="text-xs sm:text-[13px] md:text-sm font-semibold text-gray-900 leading-tight">
										{{ voucher.name }}
									</h3>
									<div v-if="voucher.description" class="text-[10px] sm:text-[11px] md:text-xs text-gray-500 mt-0.5 sm:mt-1 leading-relaxed" v-html="voucher.description"></div>
								</div>
							</div>
						</div>
					</TransitionGroup>
				</div>
			</div>
		</Transition>

		<!-- Trigger Button -->
		<button
			@click="showPanel = !showPanel"
			class="voucher-trigger flex items-center gap-1.5 sm:gap-2 bg-white px-2.5 py-1.5 sm:px-3 sm:py-2 md:px-4 md:py-2.5 rounded-full shadow-lg border border-pink-100 hover:shadow-xl transition-all duration-300"
			:class="{ 'ring-2 ring-pink-300': showPanel }"
		>
			<!-- Gift Box Icon with animation -->
			<span class="gift-icon relative text-base sm:text-lg md:text-xl">
				<!-- Closed gift box -->
				<span v-if="!showPanel" class="gift-closed">🎁</span>
				<!-- Open gift box with fireworks -->
				<span v-else class="gift-open">
					🎊
					<!-- Fireworks particles -->
					<span class="firework firework-1">✨</span>
					<span class="firework firework-2">⭐</span>
					<span class="firework firework-3">🎉</span>
					<span class="firework firework-4">✨</span>
				</span>
			</span>
			<span class="text-[11px] sm:text-xs md:text-sm font-medium text-gray-700">
				<span class="hidden sm:inline">{{ __('Offers when registering') }}</span>
				<span class="sm:hidden">{{ __('Offers') }}</span>
			</span>
			<!-- Badge showing voucher count -->
			<span class="flex items-center justify-center w-4 h-4 sm:w-[18px] sm:h-[18px] md:w-5 md:h-5 bg-pink-500 text-white text-[9px] sm:text-[10px] md:text-xs font-bold rounded-full">
				{{ vouchers.length }}
			</span>
		</button>
	</div>
</template>

<script>
export default {
	name: 'FloatingVoucher',
	props: {
		vouchers: {
			type: Array,
			default: () => []
		}
	},
	data() {
		return {
			showPanel: false
		};
	}
};
</script>

<style scoped>
/* ===== ANIMATIONS ===== */

/* Gift icon animations */
.gift-icon {
	display: inline-flex;
	align-items: center;
	justify-content: center;
}

.gift-closed {
	animation: shake-gift 1.5s ease-in-out infinite;
	display: inline-block;
}

@keyframes shake-gift {
	0%, 100% { transform: rotate(0deg) scale(1); }
	10%, 30% { transform: rotate(-8deg) scale(1.05); }
	20%, 40% { transform: rotate(8deg) scale(1.05); }
	50% { transform: rotate(0deg) scale(1); }
}

.gift-open {
	position: relative;
	display: inline-block;
	animation: pop-open 0.4s ease-out;
}

@keyframes pop-open {
	0% { transform: scale(0.5); }
	50% { transform: scale(1.3); }
	100% { transform: scale(1); }
}

/* Firework particles */
.firework {
	position: absolute;
	font-size: 0.6em;
	animation: firework-burst 1s ease-out forwards;
	opacity: 0;
}

.firework-1 { animation-delay: 0s; }
.firework-2 { animation-delay: 0.1s; }
.firework-3 { animation-delay: 0.2s; }
.firework-4 { animation-delay: 0.3s; }

.firework-1 { animation-name: firework-1; }
.firework-2 { animation-name: firework-2; }
.firework-3 { animation-name: firework-3; }
.firework-4 { animation-name: firework-4; }

@keyframes firework-1 {
	0% { opacity: 0; transform: translate(0, 0) scale(0); }
	20% { opacity: 1; transform: translate(-12px, -15px) scale(1); }
	100% { opacity: 0; transform: translate(-18px, -25px) scale(0.5); }
}

@keyframes firework-2 {
	0% { opacity: 0; transform: translate(0, 0) scale(0); }
	20% { opacity: 1; transform: translate(12px, -15px) scale(1); }
	100% { opacity: 0; transform: translate(18px, -25px) scale(0.5); }
}

@keyframes firework-3 {
	0% { opacity: 0; transform: translate(0, 0) scale(0); }
	20% { opacity: 1; transform: translate(0, -18px) scale(1.2); }
	100% { opacity: 0; transform: translate(0, -30px) scale(0.5); }
}

@keyframes firework-4 {
	0% { opacity: 0; transform: translate(0, 0) scale(0); }
	20% { opacity: 1; transform: translate(-8px, -10px) scale(1); }
	100% { opacity: 0; transform: translate(-15px, -20px) scale(0.5); }
}

/* Trigger button pulse animation */
.voucher-trigger {
	animation: pulse-glow 1.5s ease-in-out infinite;
	will-change: box-shadow;
}

@keyframes pulse-glow {
	0%, 100% { box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25); }
	50% { box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4); }
}

/* ===== TRANSITIONS ===== */

/* Voucher panel slide-up */
.voucher-panel-enter-active { transition: all 0.35s ease-out; }
.voucher-panel-leave-active { transition: all 0.25s ease-in; }
.voucher-panel-enter-from { opacity: 0; transform: translateY(16px); }
.voucher-panel-leave-to { opacity: 0; transform: translateY(8px); }

/* Stacking card animations */
.stack-card-enter-active { transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1); }
.stack-card-leave-active { transition: all 0.3s ease-in; }
.stack-card-enter-from { opacity: 0; transform: translateY(20px) scale(0.95); }
.stack-card-leave-to { opacity: 0; transform: translateY(-10px) scale(0.95); }
.stack-card-move { transition: transform 0.4s ease; }

/* ===== VOUCHER CARD ===== */
.voucher-card {
	transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.voucher-card:hover {
	transform: scale(1.02);
}

/* ===== VOUCHER PANEL ===== */
.voucher-panel {
	scrollbar-width: thin;
	scrollbar-color: rgba(0, 0, 0, 0.1) transparent;
}
.voucher-panel::-webkit-scrollbar { width: 4px; }
.voucher-panel::-webkit-scrollbar-track { background: transparent; }
.voucher-panel::-webkit-scrollbar-thumb { 
	background: rgba(0, 0, 0, 0.1); 
	border-radius: 4px; 
}
.voucher-panel::-webkit-scrollbar-thumb:hover { 
	background: rgba(0, 0, 0, 0.2); 
}

/* ===== RESPONSIVE ADJUSTMENTS ===== */

/* Mobile - reduce animation intensity */
@media (max-width: 639px) {
	@keyframes shake-gift {
		0%, 100% { transform: rotate(0deg) scale(1); }
		15%, 35% { transform: rotate(-5deg) scale(1.02); }
		25%, 45% { transform: rotate(5deg) scale(1.02); }
		50% { transform: rotate(0deg) scale(1); }
	}
	@keyframes pulse-glow {
		0%, 100% { box-shadow: 0 2px 8px rgba(59, 130, 246, 0.2); }
		50% { box-shadow: 0 3px 12px rgba(59, 130, 246, 0.35); }
	}
	.voucher-card:hover { transform: scale(1.015); }
	.firework { font-size: 0.5em; }
}

/* Tablet and up */
@media (min-width: 768px) {
	@keyframes pulse-glow {
		0%, 100% { box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3); }
		50% { box-shadow: 0 6px 25px rgba(59, 130, 246, 0.45); }
	}
}

/* Touch devices - disable hover effects */
@media (hover: none) {
	.voucher-card:hover { transform: none; }
	.voucher-trigger:hover { transform: none; }
}

/* Reduce motion for accessibility */
@media (prefers-reduced-motion: reduce) {
	.gift-closed,
	.gift-open,
	.firework,
	.voucher-trigger {
		animation: none;
	}
	.voucher-panel-enter-active,
	.voucher-panel-leave-active,
	.stack-card-enter-active,
	.stack-card-leave-active,
	.stack-card-move,
	.voucher-card {
		transition: none;
	}
}
</style>
