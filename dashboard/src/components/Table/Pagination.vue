<template>
	<div class="text-base">
		<!-- Phân trang -->
		<div class="mt-4 flex flex-wrap items-center justify-center gap-2">
			<!-- Nút "Trang trước" -->
			<button
				@click="changePage(currentPage - 1)"
				:disabled="currentPage === 1"
				class="rounded-md border bg-gray-100 p-2 hover:bg-gray-200 disabled:opacity-50"
			>
				<ArrowLeftIcon class="h-3 w-3" />
			</button>

			<!-- Hiển thị số trang -->
			<template v-for="page in visiblePages" :key="page">
				<button v-if="page === '...'" disabled class="px-3 py-2 text-gray-500">
					...
				</button>
				<button
					v-else
					@click="changePage(page)"
					:class="[
						'rounded-md border px-3 py-1.5',
						currentPage === page
							? 'bg-blue-500 text-white'
							: 'bg-gray-100 hover:bg-gray-200'
					]"
				>
					{{ page }}
				</button>
			</template>

			<!-- Nút "Trang sau" -->
			<button
				@click="changePage(currentPage + 1)"
				:disabled="currentPage === totalPages"
				class="rounded-md border bg-gray-100 p-2 hover:bg-gray-200 disabled:opacity-50"
			>
				<ArrowRightIcon class="h-3 w-3" />
			</button>
		</div>
	</div>
</template>

<script>
import ArrowRightIcon from '@/components/icons/ArrowRightIcon.vue';
import ArrowLeftIcon from '@/components/icons/ArrowLeftIcon.vue';

export default {
	components: {
		ArrowRightIcon,
		ArrowLeftIcon
	},
	props: {
		options: {
			type: Object,
			default: {}
		}
	},
	emits: ['updatePage'],
	computed: {
		visiblePages() {
			const total = this.options?.totalPages;
			const current = this.options?.currentPage;
			const range = 2; // Số trang hiển thị gần trang hiện tại
			let pages = [];

			if (total <= 7) {
				// Nếu tổng trang ít hơn 7, hiển thị tất cả
				pages = Array.from({ length: total }, (_, i) => i + 1);
			} else {
				// Trang đầu
				pages.push(1);

				// Dấu "..." trước phần giữa
				if (current - range > 2) {
					pages.push('...');
				}

				// Các trang ở giữa
				for (
					let i = Math.max(2, current - range);
					i <= Math.min(total - 1, current + range);
					i++
				) {
					pages.push(i);
				}

				// Dấu "..." sau phần giữa
				if (current + range < total - 1) {
					pages.push('...');
				}

				// Trang cuối
				pages.push(total);
			}

			return pages;
		},
		currentPage() {
			return this.options.currentPage;
		},
		totalPages() {
			return this.options.totalPages;
		}
	},
	methods: {
		changePage(page) {
			if (
				typeof page === 'number' &&
				page >= 1 &&
				page <= this.options?.totalPages
			) {
				this.$emit('updatePage', page);
			}
		}
	}
};
</script>
