import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { By } from '@angular/platform-browser';
import { DashboardComponent } from './dashboard';

describe('DashboardComponent', () => {
  let component: DashboardComponent;
  let fixture: ComponentFixture<DashboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule // Safely handles routing methods like logout links
      ],
      declarations: [ DashboardComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DashboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges(); // Triggers life-cycle hooks and DOM compilation
  });

  it('should create the dashboard component successfully', () => {
    expect(component).toBeTruthy();
  });

  it('should display the main metric cards inside the view grid', () => {
    const cardElements = fixture.debugElement.queryAll(By.css('.metrics-grid .card'));
    expect(cardElements.length).toBe(3); // Total, Active, and Pending procurement metrics
  });

  it('should correctly initialize recent activity data array items', () => {
    // Verifies that data elements present in the screen capture exist on initialization
    expect(component.recentActivities).toBeDefined();
    expect(component.recentActivities.length).toBeGreaterThan(0);
    expect(component.recentActivities[0].referenceId).toBe('VEN-2505-001');
  });

  it('should dynamically apply the correct CSS class based on status variant', () => {
    fixture.detectChanges();
    const statusBadges = fixture.debugElement.queryAll(By.css('.status'));
    
    // Checks that the first element features the expected 'completed' label class assignment
    expect(statusBadges[0].nativeElement.classList.contains('completed')).toBe(true);
  });

  it('should contain a distinct link layout targeting system logout operation', () => {
    const logoutBtn = fixture.debugElement.query(By.css('.logout-btn'));
    expect(logoutBtn).toBeTruthy();
    expect(logoutBtn.nativeElement.textContent).toContain('Logout');
  });
});